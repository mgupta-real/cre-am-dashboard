"""
components/charts.py
Reusable Plotly chart functions with the dark CRE dashboard theme.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from components.theme import COLORS, CHART_COLORS

# ── Shared axis / layout helpers ──────────────────────────────────────────────
_AXIS = dict(
    gridcolor=COLORS["border"],
    linecolor=COLORS["border"],
    tickfont=dict(size=11, color=COLORS["text_secondary"]),
    zerolinecolor=COLORS["border"],
)

def _base_layout(height=320, margin=None, legend_y=-0.15, showlegend=True):
    """Return a base layout dict — no yaxis/xaxis so callers can set freely."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLORS["text_secondary"], size=12),
        height=height,
        margin=margin or dict(l=10, r=10, t=10, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_secondary"], size=11),
            orientation="h",
            y=legend_y,
        ),
        showlegend=showlegend,
    )


# ── Revenue / Expense / NOI Trend ─────────────────────────────────────────────
def revenue_expense_noi_trend(month_labels, revenues, expenses, nois, height=340):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=month_labels, y=revenues, name="Total Revenue",
        line=dict(color=COLORS["accent_blue"], width=2.5),
        fill="tozeroy", fillcolor="rgba(30,111,235,0.08)",
        mode="lines+markers", marker=dict(size=4),
    ))
    fig.add_trace(go.Scatter(
        x=month_labels, y=expenses, name="Total Expenses",
        line=dict(color=COLORS["red"], width=2),
        mode="lines+markers", marker=dict(size=4),
    ))
    fig.add_trace(go.Scatter(
        x=month_labels, y=nois, name="NOI",
        line=dict(color=COLORS["accent_teal"], width=2.5),
        fill="tozeroy", fillcolor="rgba(10,223,180,0.06)",
        mode="lines+markers", marker=dict(size=4),
    ))
    fig.update_layout(
        **_base_layout(height=height, legend_y=-0.20),
        xaxis=_AXIS,
        yaxis=dict(**_AXIS, tickprefix="$", tickformat=",.0f"),
    )
    return fig


# ── NOI Margin Trend ──────────────────────────────────────────────────────────
def noi_margin_trend(month_labels, margins, height=280):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=month_labels,
        y=[m * 100 if m is not None else None for m in margins],
        name="NOI Margin",
        line=dict(color=COLORS["accent_cyan"], width=2.5),
        fill="tozeroy", fillcolor="rgba(0,194,255,0.07)",
        mode="lines+markers", marker=dict(size=4),
    ))
    fig.update_layout(
        **_base_layout(height=height, showlegend=False),
        xaxis=_AXIS,
        yaxis=dict(**_AXIS, ticksuffix="%", tickformat=".1f"),
    )
    return fig


# ── T12/T6/T3/Current comparison bar ─────────────────────────────────────────
def t_period_comparison(periods, noi_vals, noi_margins, height=300):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=periods, y=noi_vals, name="NOI ($)",
        marker_color=[COLORS["accent_blue"], COLORS["accent_cyan"],
                      COLORS["accent_teal"], COLORS["yellow"]],
        text=[f"${v:,.0f}" if v else "" for v in noi_vals],
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text_primary"]),
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=periods,
        y=[m * 100 if m is not None else None for m in noi_margins],
        name="NOI Margin (%)", mode="lines+markers",
        line=dict(color=COLORS["yellow"], width=2),
        marker=dict(size=6, color=COLORS["yellow"]),
    ), secondary_y=True)
    fig.update_yaxes(tickprefix="$", tickformat=",.0f", secondary_y=False,
                     gridcolor=COLORS["border"])
    fig.update_yaxes(ticksuffix="%", tickformat=".1f", secondary_y=True,
                     showgrid=False)
    fig.update_layout(
        **_base_layout(height=height, legend_y=-0.20),
        barmode="group",
        xaxis=_AXIS,
    )
    return fig


# ── Revenue mix donut ─────────────────────────────────────────────────────────
def revenue_mix_donut(labels, values, center_label="Total Revenue", center_val="", height=320):
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.60,
        marker=dict(colors=CHART_COLORS, line=dict(color=COLORS["bg_primary"], width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color=COLORS["text_primary"]),
        hovertemplate="%{label}: $%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(height=height, margin=dict(l=10, r=10, t=10, b=10)),
        annotations=[dict(
            text=f"<b>{center_val}</b><br><span style='font-size:11px'>{center_label}</span>",
            x=0.5, y=0.5, font=dict(size=15, color=COLORS["text_primary"]), showarrow=False,
        )],
    )
    return fig


# ── Expense mix donut ─────────────────────────────────────────────────────────
def expense_mix_donut(labels, values, center_label="Total Expenses", center_val="", height=320):
    return revenue_mix_donut(labels, values, center_label, center_val, height)


# ── NOI Bridge waterfall ──────────────────────────────────────────────────────
def noi_bridge(revenue, expenses, noi, height=320):
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "total"],
        x=["Total Revenue", "Operating Expenses", "NOI"],
        y=[revenue, -abs(expenses), noi],
        text=[f"${revenue:,.0f}", f"-${abs(expenses):,.0f}", f"${noi:,.0f}"],
        textposition="outside",
        decreasing=dict(marker_color=COLORS["red"]),
        increasing=dict(marker_color=COLORS["accent_blue"]),
        totals=dict(marker_color=COLORS["accent_teal"]),
        connector=dict(line=dict(color=COLORS["border"], width=1)),
        textfont=dict(color=COLORS["text_primary"], size=12),
    ))
    fig.update_layout(
        **_base_layout(height=height, showlegend=False),
        xaxis=_AXIS,
        yaxis=dict(**_AXIS, tickprefix="$", tickformat=",.0f"),
    )
    return fig


# ── Occupancy status donut ────────────────────────────────────────────────────
def occupancy_donut(occ_count, vac_count, notice_count, model_count, total, height=300):
    labels = ["Occupied", "Vacant", "Notice", "Model/Admin"]
    values = [occ_count, vac_count, notice_count, model_count]
    colors_map = [COLORS["accent_blue"], COLORS["red"], COLORS["yellow"], COLORS["purple"]]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=colors_map, line=dict(color=COLORS["bg_primary"], width=2)),
        textinfo="label+percent",
        textfont=dict(size=11),
        hovertemplate="%{label}: %{value} units (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(height=height, margin=dict(l=0, r=0, t=10, b=10)),
        annotations=[dict(
            text=f"<b>{total}</b><br><span style='font-size:10px'>Total Units</span>",
            x=0.5, y=0.5, font=dict(size=16, color=COLORS["text_primary"]), showarrow=False,
        )],
    )
    return fig


# ── Unit mix horizontal bar ───────────────────────────────────────────────────
def unit_mix_bar(unit_types, counts, height=280):
    fig = go.Figure(go.Bar(
        y=unit_types, x=counts, orientation="h",
        marker_color=CHART_COLORS[:len(unit_types)],
        text=[f"{c}" for c in counts],
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text_primary"]),
    ))
    fig.update_layout(
        **_base_layout(height=height, margin=dict(l=80, r=40, t=10, b=10), showlegend=False),
        xaxis=dict(**_AXIS),
        yaxis=dict(tickfont=dict(size=11, color=COLORS["text_primary"]), gridcolor="rgba(0,0,0,0)"),
    )
    return fig


# ── Avg In-Place vs Market Rent grouped bar ───────────────────────────────────
def rent_comparison_bar(unit_types, inplace_rents, market_rents, height=300):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="In-Place Rent", x=unit_types, y=inplace_rents,
        marker_color=COLORS["accent_blue"],
        text=[f"${v:,.0f}" for v in inplace_rents],
        textposition="outside", textfont=dict(size=10),
    ))
    fig.add_trace(go.Bar(
        name="Market Rent", x=unit_types, y=market_rents,
        marker_color=COLORS["accent_cyan"],
        text=[f"${v:,.0f}" for v in market_rents],
        textposition="outside", textfont=dict(size=10),
    ))
    fig.update_layout(
        barmode="group",
        **_base_layout(height=height, legend_y=-0.20),
        yaxis=dict(**_AXIS, tickprefix="$", tickformat=",.0f"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11)),
    )
    return fig


# ── Lease expirations line ────────────────────────────────────────────────────
def lease_expiration_chart(months, counts, height=280):
    fig = go.Figure(go.Scatter(
        x=months, y=counts,
        mode="lines+markers+text",
        line=dict(color=COLORS["accent_blue"], width=2.5),
        marker=dict(size=7, color=COLORS["accent_cyan"]),
        text=[str(c) for c in counts],
        textposition="top center",
        textfont=dict(size=11, color=COLORS["text_primary"]),
        fill="tozeroy", fillcolor="rgba(30,111,235,0.08)",
    ))
    fig.update_layout(
        **_base_layout(height=height, showlegend=False),
        yaxis=dict(**_AXIS),
        xaxis=dict(**_AXIS, tickangle=-30),
    )
    return fig


# ── Expiry buckets bar ────────────────────────────────────────────────────────
def expiry_buckets_bar(buckets, counts, height=280):
    colors = [
        COLORS["red"]          if ("0–3" in b or "Expired" in b) else
        COLORS["yellow"]       if "3–6" in b else
        COLORS["accent_blue"]
        for b in buckets
    ]
    fig = go.Figure(go.Bar(
        x=buckets, y=counts, marker_color=colors,
        text=counts, textposition="outside",
        textfont=dict(size=11, color=COLORS["text_primary"]),
    ))
    fig.update_layout(
        **_base_layout(height=height, showlegend=False),
        yaxis=dict(**_AXIS),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10)),
    )
    return fig


# ── Rent per SF bar ───────────────────────────────────────────────────────────
def rent_per_sf_bar(unit_types, rpsf_vals, height=280):
    fig = go.Figure(go.Bar(
        x=unit_types, y=rpsf_vals,
        marker_color=CHART_COLORS[:len(unit_types)],
        text=[f"${v:.2f}" if v else "" for v in rpsf_vals],
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text_primary"]),
    ))
    fig.update_layout(
        **_base_layout(height=height, showlegend=False),
        yaxis=dict(**_AXIS, tickprefix="$", tickformat=".2f"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    return fig


# ── Capex by category bar ─────────────────────────────────────────────────────
def capex_by_category(categories, budgets, actuals, height=320):
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Budget", x=categories, y=budgets,
                         marker_color=COLORS["accent_blue"]))
    fig.add_trace(go.Bar(name="Actual", x=categories, y=actuals,
                         marker_color=COLORS["accent_teal"]))
    fig.update_layout(
        barmode="group",
        **_base_layout(height=height, margin=dict(l=10, r=10, t=10, b=60), legend_y=-0.30),
        yaxis=dict(**_AXIS, tickprefix="$", tickformat=",.0f"),
        xaxis=dict(tickangle=-30, tickfont=dict(size=10)),
    )
    return fig
