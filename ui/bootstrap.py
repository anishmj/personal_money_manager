import html
from pathlib import Path
from typing import Mapping, Sequence

import streamlit as st


BOOTSTRAP_CSS_PATH = (
    Path(__file__).resolve().parent.parent
    / "static"
    / "bootstrap.min.css"
)

ACCENT_CLASSES = {
    "primary": "border-primary",
    "success": "border-success",
    "danger": "border-danger"
}


@st.cache_data(show_spinner=False)
def _load_bootstrap_css():
    if not BOOTSTRAP_CSS_PATH.is_file():
        raise FileNotFoundError(
            f"Bootstrap stylesheet is missing: {BOOTSTRAP_CSS_PATH}"
        )
    return BOOTSTRAP_CSS_PATH.read_text(encoding="utf-8")


def render_dashboard_kpis(cards: Sequence[Mapping[str, str]]):
    """Render responsive Bootstrap KPI cards in an isolated HTML component."""
    rendered_cards = []
    for card in cards:
        accent = ACCENT_CLASSES.get(card["accent"])
        if accent is None:
            raise ValueError(f"Unsupported KPI accent: {card['accent']}")

        title = html.escape(card["title"])
        value = html.escape(card["value"])
        detail = html.escape(card.get("detail", ""))
        detail_markup = (
            f'<p class="card-text small text-secondary mb-0">{detail}</p>'
            if detail else ""
        )

        rendered_cards.append(
            f"""
            <div class="col">
                <article class="card h-100 border-0 border-start border-4 {accent} shadow-sm">
                    <div class="card-body p-3 p-md-4">
                        <p class="small fw-semibold text-secondary mb-2">{title}</p>
                        <p class="h4 fw-bold text-primary mb-2 text-break">{value}</p>
                        {detail_markup}
                    </div>
                </article>
            </div>
            """
        )

    document = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
          {_load_bootstrap_css()}
          :root {{
            --bs-primary: #172B4D;
            --bs-primary-rgb: 23, 43, 77;
            --bs-success: #16A36A;
            --bs-success-rgb: 22, 163, 106;
            --bs-danger: #E05252;
            --bs-danger-rgb: 224, 82, 82;
            --bs-secondary-color: #64748B;
          }}
          html, body {{ margin: 0; padding: 0; background: transparent; }}
          body {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }}
          .card {{ border-radius: 0.8rem; }}
          .card-body {{ min-width: 0; }}
          .h4 {{ font-size: clamp(1.05rem, 3.2vw, 1.5rem); }}
          @media (min-width: 900px) {{
            .row-cols-lg-3 > * {{ flex: 0 0 auto; width: 33.33333333%; }}
          }}
        </style>
      </head>
      <body>
        <main class="container-fluid p-0 overflow-hidden">
          <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
            {''.join(rendered_cards)}
          </div>
        </main>
      </body>
    </html>
    """

    st.iframe(
        document,
        height="content",
        alt="Financial dashboard KPI cards"
    )
