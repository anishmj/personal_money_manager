
import plotly.express as px
import pandas as pd


def period_income_expense_chart(df, start_date, end_date, period_mode):
    """Create a period-aware income vs expenses chart."""
    data = df.copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")
    data["Type"] = data["Type"].astype(str).str.strip().str.title()
    data = data.dropna(subset=["Date", "Amount"])

    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    if period_mode == "Monthly":
        selected_month = start.to_period("M")
        month_end = selected_month.end_time.normalize()
        first_month = (selected_month - 5).start_time
        trend = data[(data["Date"] >= first_month) & (data["Date"] <= month_end)].copy()
        trend["Period"] = trend["Date"].dt.to_period("M").astype(str)

        summary = (
            trend.groupby(["Period", "Type"])["Amount"].sum().reset_index()
            if not trend.empty else pd.DataFrame(columns=["Period", "Type", "Amount"])
        )
        x_title = "Month"

    else:
        period = data[(data["Date"] >= start) & (data["Date"] <= end)].copy()
        period["Period"] = period["Date"].dt.strftime("%d %b")
        summary = (
            period.groupby(["Period", "Type"])["Amount"].sum().reset_index()
            if not period.empty else pd.DataFrame(columns=["Period", "Type", "Amount"])
        )
        x_title = "Date"

    fig = px.bar(
        summary,
        x="Period",
        y="Amount",
        color="Type",
        barmode="group",
        text_auto=".2s",
        color_discrete_map={"Income": "#16A34A", "Expense": "#DC2626"}
    )
    fig.update_layout(
        height=390,
        xaxis_title=x_title,
        yaxis_title="Amount",
        legend_title_text="",
        bargap=0.25,
        template="plotly_white",
        font={"family": "Inter, sans-serif", "color": "#334155"},
        title_font={"color": "#172554"},
        legend={"font": {"color": "#334155"}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={
            "type": "category",
            "showgrid": False,
            "tickfont": {"color": "#475569"},
            "title_font": {"color": "#334155"}
        },
        yaxis={
            "gridcolor": "#E8EDF4",
            "zerolinecolor": "#D8E0EC",
            "rangemode": "tozero",
            "tickprefix": "₹",
            "tickformat": ",.0f",
            "tickfont": {"color": "#475569"},
            "title_font": {"color": "#334155"}
        },
        margin={"l": 44, "r": 12, "t": 20, "b": 44}
    )
    fig.update_traces(
        hovertemplate="%{x}<br>%{fullData.name}: ₹%{y:,.2f}<extra></extra>"
    )
    return fig


def expense_category_summary(df, start_date, end_date):
    """Build the top-10 expense category summary, including Others."""
    data = df.copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")
    data["Type"] = data["Type"].astype(str).str.strip().str.title()
    data = data[
        (data["Date"] >= pd.Timestamp(start_date)) &
        (data["Date"] <= pd.Timestamp(end_date)) &
        (data["Type"] == "Expense")
    ].copy()

    if data.empty:
        return pd.DataFrame(columns=["Category", "Amount", "Percentage"])

    summary = (
        data.groupby("Category", dropna=False)["Amount"].sum()
        .reset_index()
        .sort_values("Amount", ascending=False)
    )
    summary["Category"] = summary["Category"].fillna("Uncategorized").replace("", "Uncategorized")
    summary = summary.groupby("Category", as_index=False)["Amount"].sum()
    summary = summary.sort_values("Amount", ascending=False)

    if len(summary) > 10:
        top = summary.head(10).copy()
        others_amount = float(summary.iloc[10:]["Amount"].sum())
        if others_amount > 0:
            top = pd.concat(
                [top, pd.DataFrame([{"Category": "Others", "Amount": others_amount}])],
                ignore_index=True
            )
        summary = top

    total = float(summary["Amount"].sum())
    summary["Percentage"] = summary["Amount"].div(total).mul(100).fillna(0)
    summary.attrs["start_date"] = pd.Timestamp(start_date)
    summary.attrs["end_date"] = pd.Timestamp(end_date)
    return summary


def expense_category_pie_chart(df, start_date, end_date):
    """Create a top-10 pie chart, grouping the remaining categories as Others."""
    summary = expense_category_summary(df, start_date, end_date)
    if summary.empty:
        return None

    fig = px.pie(
        summary,
        names="Category",
        values="Amount",
        custom_data=["Amount", "Percentage"],
        color_discrete_sequence=[
            "#4F46E5", "#0EA5E9", "#10B981", "#F59E0B",
            "#F43F5E", "#8B5CF6", "#14B8A6", "#64748B",
            "#E879F9", "#22C55E", "#FB7185"
        ]
    )
    fig.update_traces(
        texttemplate="%{percent:.1%}",
        textposition="auto",
        sort=False,
        hovertemplate="Category: %{label}<br>Amount: ₹%{custom_data[0]:,.2f}<br>Percentage: %{custom_data[1]:.1f}%<extra></extra>",
        marker={"line": {"color": "#FFFFFF", "width": 1}}
    )
    fig.update_layout(
        height=370,
        showlegend=True,
        template="plotly_white",
        font={"family": "Inter, sans-serif", "color": "#334155"},
        title_font={"color": "#172554"},
        paper_bgcolor="rgba(0,0,0,0)",
        margin={"l": 12, "r": 12, "t": 12, "b": 44},
        legend={
            "orientation": "h",
            "y": -0.08,
            "font": {"color": "#334155", "size": 12},
            "itemwidth": 140
        }
    )
    return fig


# Backward-compatible alias for existing imports and tests.
def expense_category_donut_chart(df, start_date, end_date):
    return expense_category_pie_chart(df, start_date, end_date)


def period_daily_expense_chart(df, start_date, end_date):
    """Create a zero-filled daily expense chart for an inclusive period."""
    start = pd.Timestamp(start_date).normalize()
    end = pd.Timestamp(end_date).normalize()
    dates = pd.DataFrame({
        "Date": pd.date_range(start=start, end=end, freq="D")
    })

    data = df.copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce").dt.normalize()
    data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")
    data["Type"] = data["Type"].astype(str).str.strip().str.title()

    expenses = data[
        (data["Date"] >= start) &
        (data["Date"] <= end) &
        (data["Type"] == "Expense")
    ].copy()

    daily = (
        expenses.groupby("Date")["Amount"].sum().reset_index()
        if not expenses.empty else pd.DataFrame(columns=["Date", "Amount"])
    )
    daily = dates.merge(daily, on="Date", how="left")
    daily["Amount"] = daily["Amount"].fillna(0)

    fig = px.area(
        daily,
        x="Date",
        y="Amount",
        markers=True
    )
    fig.update_traces(
        line_color="#DC2626",
        fillcolor="rgba(220,38,38,0.12)",
        hovertemplate="%{x|%d %b %Y}<br>Expense: ₹%{y:,.2f}<extra></extra>"
    )
    fig.update_layout(
        height=370,
        xaxis_title="Date",
        yaxis_title="Amount",
        hovermode="x",
        template="plotly_white",
        font={"family": "Inter, sans-serif", "color": "#334155"},
        title_font={"color": "#172554"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={
            "showgrid": False,
            "tickformat": "%d %b",
            "nticks": 6,
            "tickfont": {"color": "#475569"},
            "title_font": {"color": "#334155"}
        },
        yaxis={
            "gridcolor": "#E8EDF4",
            "zerolinecolor": "#D8E0EC",
            "rangemode": "tozero",
            "tickprefix": "₹",
            "tickformat": ",.0f",
            "tickfont": {"color": "#475569"},
            "title_font": {"color": "#334155"}
        },
        margin={"l": 44, "r": 12, "t": 12, "b": 44}
    )
    return fig


def income_expense_chart(df):

    monthly = df.copy()

    monthly["Month"] = monthly["Date"].dt.to_period(
        "M"
    ).astype(str)

    summary = (
        monthly.groupby(["Month", "Type"])["Amount"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        summary,
        x="Month",
        y="Amount",
        color="Type",
        barmode="group",
        title="Monthly Income vs Expenses",
        text_auto=".2s"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount (INR)"
    )

    return fig


def category_expense_chart(df):

    expenses = df[
        df["Type"] == "Expense"
    ]

    summary = (
        expenses.groupby("Category")["Amount"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        summary,
        names="Category",
        values="Amount",
        title="Category-wise Spending"
    )

    return fig


def daily_expense_chart(df):

    expenses = df[
        df["Type"] == "Expense"
    ].copy()

    daily = (
        expenses.groupby(
            expenses["Date"].dt.date
        )["Amount"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        daily,
        x="Date",
        y="Amount",
        markers=True,
        title="Daily Expense Trend"
    )

    return fig


def savings_trend_chart(df, initial_balance):

    data = df.copy()

    data["Net Amount"] = data.apply(
        lambda row: (
            row["Amount"]
            if row["Type"] == "Income"
            else -row["Amount"]
        ),
        axis=1
    )

    data = data.sort_values(
        ["Date", "Created At"],
        kind="stable"
    )

    data["Balance"] = (
        initial_balance + data["Net Amount"].cumsum()
    )

    fig = px.line(
        data,
        x="Date",
        y="Balance",
        markers=True,
        title="Balance Trend"
    )

    return fig


def top_spending_categories(df):

    expenses = df[
        df["Type"] == "Expense"
    ]

    summary = (
        expenses.groupby("Category")["Amount"]
        .sum()
        .reset_index()
        .sort_values("Amount", ascending=True)
        .tail(5)
    )

    fig = px.bar(
        summary,
        x="Amount",
        y="Category",
        orientation="h",
        title="Top 5 Spending Categories",
        text_auto=".2s"
    )

    return fig
