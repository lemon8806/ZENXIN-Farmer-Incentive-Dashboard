from html import escape
from textwrap import wrap

import plotly.express as px
import streamlit as st

from data_loader import load_data

st.set_page_config(page_title="Farmer Incentive Dashboard", layout="wide")
st.markdown("""
<style>
    /* The selected chips scroll inside a fixed-height field; the menu is a portal. */
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div {
        height: 120px;
        min-height: 120px;
        max-height: 120px;
        overflow-y: auto;
        align-content: flex-start;
    }
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {
        min-height: 120px;
    }
    section[data-testid="stSidebar"] .stMultiSelect .react-aria-ComboBox > [role="group"] {
        height: 120px;
        min-height: 120px;
        max-height: 120px;
    }
    section[data-testid="stSidebar"] .stMultiSelect [data-testid="stMultiSelectTagsContainer"] {
        height: 100%;
        max-height: 100%;
        overflow-y: auto;
        align-content: flex-start;
    }
    div[data-testid="stMetric"],
    div[class*="st-key-chart_card_"] {
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05),
                    0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border-radius: 12px;
        padding: 1.5rem;
        background-color: #FFFFFF;
        color: #202124;
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetricValue"],
    div[class*="st-key-chart_card_"] h3 { color: #202124; }
    div[data-testid="stMetricValue"] { font-weight: 700; }
</style>
""", unsafe_allow_html=True)
st.title("Farmer Incentive Dashboard")
st.caption("Shipment and incentive performance across your farms")

try:
    data = load_data()
except Exception as exc:
    st.error(f"Unable to load Clean Data: {exc}")
    st.stop()

if data.empty:
    st.warning("No rows have a valid incentive amount.")
    st.stop()

valid_dates = data["Harvest Date"].dropna()
if valid_dates.empty:
    st.warning("No valid harvest dates are available.")
    st.stop()

with st.sidebar:
    st.header("Filters")
    start, end = valid_dates.min().date(), valid_dates.max().date()
    st.subheader("Harvest Date")
    date_mode = st.radio("Date selection mode", ["Date Range", "Specific Dates"], horizontal=True, label_visibility="collapsed")
    if date_mode == "Date Range":
        date_range = st.date_input("Date Range", value=(start, end), min_value=start, max_value=end)
    else:
        dates = sorted(valid_dates.dt.date.unique().tolist())
        selected_dates = st.multiselect("Specific Dates", dates, default=dates, format_func=lambda d: d.strftime("%d %b %Y"))
    farms = sorted(data["Farm"].unique().tolist())
    groups = sorted(data["Group"].unique().tolist())
    crops = sorted(data["Crop"].unique().tolist())
    selected_farms = st.multiselect("Farm", farms, default=farms)
    selected_groups = st.multiselect("Group", groups, default=groups)
    selected_crops = st.multiselect("Crop", crops, default=crops)

if date_mode == "Date Range":
    if len(date_range) != 2:
        st.info("Select both the start and end dates.")
        st.stop()
    date_mask = data["Harvest Date"].dt.date.between(date_range[0], date_range[1])
else:
    date_mask = data["Harvest Date"].dt.date.isin(selected_dates)
filtered = data.loc[
    date_mask
    & data["Farm"].isin(selected_farms)
    & data["Group"].isin(selected_groups)
    & data["Crop"].isin(selected_crops)
]
shipment = filtered["Shipment"].sum()
incentive = filtered["Incentive"].sum()
columns = st.columns(3)
columns[0].metric("TOTAL SHIPMENT", f"{shipment:,.2f} KG", border=True)
columns[1].metric("TOTAL INCENTIVE PAID", f"RM {incentive:,.2f}", border=True)
columns[2].metric("AVERAGE INCENTIVE PAID PER KG", f"RM {incentive / shipment:,.2f} PER KG" if shipment else "—", border=True)

if filtered.empty:
    st.info("No data matches the selected filters.")
    st.stop()

crop_totals = filtered.groupby("Crop", as_index=False)["Shipment"].sum().sort_values("Shipment", ascending=False)
farm_totals = filtered.groupby("Farm", as_index=False)["Shipment"].sum().sort_values("Shipment", ascending=False)
group_totals = filtered.groupby("Group", as_index=False)["Incentive"].sum().sort_values("Incentive", ascending=False)

with st.container(key="chart_card_crops"):
    st.subheader("Top Ranked Crops by Shipment")
    fig = px.bar(crop_totals, x="Shipment", y="Crop", text="Shipment", orientation="h", labels={"Shipment": "Shipment (kg)"}, color_discrete_sequence=["#4285f4"])
    fig.update_traces(texttemplate="%{text:,.1f}", textposition="outside", cliponaxis=False)
    # Keep the original crop names for grouping and hover; wrap only axis labels.
    crop_names = crop_totals["Crop"].tolist()
    wrapped_names = ["<br>".join(escape(line) for line in wrap(name, width=25, break_long_words=False, break_on_hyphens=False)) for name in crop_names]
    fig.update_layout(yaxis={"categoryorder": "total ascending", "tickmode": "array", "tickvals": crop_names, "ticktext": wrapped_names, "tickfont": {"size": 11}, "title": {"standoff": 55}, "automargin": True}, height=max(380, 44 * len(crop_totals) + 100), margin=dict(l=280, r=90), paper_bgcolor="white", plot_bgcolor="white", font_color="#202124", uniformtext=dict(mode="show"))
    if crop_totals["Shipment"].max() > 0:
        fig.update_xaxes(range=[min(0, crop_totals["Shipment"].min() * 1.2), crop_totals["Shipment"].max() * 1.18])
    st.plotly_chart(fig, width="stretch", theme=None)

left, right = st.columns(2)
with left:
    with st.container(key="chart_card_farm"):
        st.subheader("Total Shipment by Farm")
        fig = px.bar(farm_totals, x="Farm", y="Shipment", text="Shipment", labels={"Shipment": "Shipment (kg)"}, color_discrete_sequence=["#4285f4"])
        fig.update_traces(texttemplate="%{text:,.1f}", textposition="outside", cliponaxis=False)
        fig.update_layout(margin=dict(t=45), paper_bgcolor="white", plot_bgcolor="white", font_color="#202124", uniformtext=dict(mode="show"))
        if farm_totals["Shipment"].max() > 0:
            fig.update_yaxes(range=[min(0, farm_totals["Shipment"].min() * 1.2), farm_totals["Shipment"].max() * 1.18])
        st.plotly_chart(fig, width="stretch", theme=None)
with right:
    with st.container(key="chart_card_incentive"):
        st.subheader("Incentive Distribution")
        if (group_totals["Incentive"] < 0).any():
            fig = px.bar(group_totals, x="Group", y="Incentive", labels={"Incentive": "Incentive (RM)"}, color_discrete_sequence=["#ff9100"])
        else:
            fig = px.pie(group_totals, names="Group", values="Incentive", hole=0.45)
            fig.update_traces(
                textposition="outside",
                texttemplate="<b>%{label}</b><br>RM %{value:,.2f}<br>(%{percent:.1%})",
                textfont=dict(size=11),
            )
            fig.update_layout(showlegend=False, height=650, margin=dict(l=100, r=100, t=30, b=30))
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white", font_color="#202124")
        st.plotly_chart(fig, width="stretch", theme=None)
