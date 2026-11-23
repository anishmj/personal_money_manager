from pathlib import Path
import re
from typing import Any, Callable, Optional, Sequence

import streamlit as st
import streamlit.components.v1 as components


_COMPONENT = components.declare_component(
    "native_dropdown",
    path=str(Path(__file__).resolve().parent / "components" / "native_select" / "dist")
)


def native_selectbox(
    label: str,
    options: Sequence[Any],
    index: int = 0,
    format_func: Callable[[Any], str] = str,
    key: Optional[str] = None
) -> Any:
    """Render a native HTML select that returns its selected option to Python."""
    values = list(options)
    if not values:
        raise ValueError(f"{label} requires at least one option.")
    if index < 0 or index >= len(values):
        raise ValueError(f"Selected index for {label} is out of range.")

    component_key = key or "native-select-" + re.sub(
        r"[^a-z0-9]+", "-", label.casefold()
    ).strip("-")
    default_value = values[index]
    selected_value = st.session_state.get(component_key, default_value)
    if selected_value not in values:
        selected_value = default_value
        if component_key in st.session_state:
            st.session_state[component_key] = default_value

    result = _COMPONENT(
        label=label,
        options=[str(format_func(value)) for value in values],
        values=values,
        selected_value=selected_value,
        key=component_key,
        default=default_value
    )
    return result if result in values else default_value
