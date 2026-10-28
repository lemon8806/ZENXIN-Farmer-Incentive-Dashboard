from html import escape
from textwrap import wrap

import plotly.express as px
import streamlit as st

from data_loader import load_data

st.set_page_config(page_title="Farmer Incentive Dashboard", layout="wide")
st.markdown("""
<style>
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div { background: #F8FAFC; }
    section[data-testid="stSidebar"] div[class*="st-key-filter_card_"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 0.9rem;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
    }
    section[data-testid="stSidebar"] .filter-heading {
        color: #0F172A; font-size: 1.3rem; font-weight: 750;
        letter-spacing: -0.02em; margin-bottom: 0.15rem;
    }
    section[data-testid="stSidebar"] .filter-subtitle {
        color: #64748B; font-size: 0.82rem; margin-bottom: 0.5rem;
    }
    section[data-testid="stSidebar"] .filter-title {
        display: flex; justify-content: space-between; align-items: center;
        color: #1E293B; font-size: 0.9rem; font-weight: 650;
    }
    section[data-testid="stSidebar"] .filter-count {
        background: #EFF6FF; color: #1D4ED8; border: 1px solid #DBEAFE;
        border-radius: 999px; padding: 2px 8px; font-size: 0.72rem;
    }
    section[data-testid="stSidebar"] .stMultiSelect [data-tag],
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
        background: #EFF6FF !important; color: #1D4ED8 !important;
        border: 1px solid #BFDBFE; border-radius: 6px; font-size: 12px;
    }
    section[data-testid="stSidebar"] .stMultiSelect [data-tag] button,
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] button {
        color: #1D4ED8 !important;
    }
    section[data-testid="stSidebar"] .stMultiSelect [data-testid="stMultiSelectTagsContainer"]::-webkit-scrollbar,
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div::-webkit-scrollbar { width: 5px; }
    section[data-testid="stSidebar"] .stMultiSelect [data-testid="stMultiSelectTagsContainer"]::-webkit-scrollbar-thumb,
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div::-webkit-scrollbar-thumb {
        background: #CBD5E1; border-radius: 999px;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {
        background: #F1F5F9; border-radius: 10px; padding: 4px; gap: 4px;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label {
        border-radius: 7px; padding: 5px 8px; background: #FFFFFF;
    }
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
    .mobile-filter-hint, .st-key-mobile_crop_chart, .st-key-mobile_incentive_chart { display: none; }
    @media (max-width: 768px) {
        section[data-testid="stMain"] [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        section[data-testid="stMain"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            width: 100% !important; flex: 1 1 100% !important; min-width: 0 !important;
        }
        section[data-testid="stMain"] .block-container { padding: 1rem 0.75rem 2rem; }
        div[data-testid="stMetric"], div[class*="st-key-chart_card_"] { padding: 1rem; }
        div[data-testid="stMetricValue"] { font-size: clamp(1.35rem, 6vw, 2rem); }
        .mobile-filter-hint { display: block; color: #475569; font-size: 0.86rem; margin: 0 0 0.75rem; }
        [data-testid="stSidebarCollapsedControl"] button { min-width: 44px; min-height: 44px; background: #EFF6FF; border-radius: 10px; }
        section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div,
        section[data-testid="stSidebar"] .stMultiSelect .react-aria-ComboBox > [role="group"] {
            height: 180px; min-height: 180px; max-height: 180px;
        }
        section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] { min-height: 180px; }
        section[data-testid="stSidebar"] .stMultiSelect [data-tag],
        section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] { min-height: 32px; margin: 3px; }
        section[data-testid="stSidebar"] .stMultiSelect [data-tag] button { min-width: 32px; min-height: 32px; }
        section[data-testid="stSidebar"] .stMultiSelect [data-testid="stMultiSelectTagsContainer"]::-webkit-scrollbar,
        section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div::-webkit-scrollbar { width: 8px; }
        .st-key-desktop_crop_chart, .st-key-desktop_incentive_chart { display: none; }
        .st-key-mobile_crop_chart, .st-key-mobile_incentive_chart { display: block; }
    }
</style>
""", unsafe_allow_html=True)
st.title("Farmer Incentive Dashboard")
st.caption("Shipment and incentive performance across your farms")
st.markdown('<div class="mobile-filter-hint">💡 Tap the top-left arrow to open filters.</div>', unsafe_allow_html=True)

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
    start, end = valid_dates.min().date(), valid_dates.max().date()
    dates = sorted(valid_dates.dt.date.unique().tolist())
    farms = sorted(data["Farm"].unique().tolist())
    groups = sorted(data["Group"].unique().tolist())
    crops = sorted(data["Crop"].unique().tolist())
    defaults = {"filter_mode": "Date Range", "filter_range": (start, end), "filter_dates": dates,
                "filter_farms": farms, "filter_groups": groups, "filter_crops": crops}
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    def set_filter(key, value):
        st.session_state[key] = value

    def reset_filters():
        for key, value in defaults.items():
            st.session_state[key] = value

    st.markdown('<div class="filter-heading">⚑ &nbsp;Filters</div><div class="filter-subtitle">Refine the dashboard to explore your data.</div>', unsafe_allow_html=True)
    st.button("↺  Reset All Filters", on_click=reset_filters, width="stretch", type="primary")
    status = st.empty()

    with st.container(key="filter_card_date"):
        st.markdown('<div class="filter-title">📅 &nbsp;Harvest Date</div>', unsafe_allow_html=True)
        date_mode = st.radio("Date selection mode", ["Date Range", "Specific Dates"], key="filter_mode", horizontal=True, label_visibility="collapsed", format_func=lambda mode: "📅 Range" if mode == "Date Range" else "📌 Specific")
        if date_mode == "Date Range":
            date_range = st.date_input("Date Range", min_value=start, max_value=end, key="filter_range", persist_state="session")
        else:
            st.markdown(f'<div class="filter-title">Dates <span class="filter-count">{len(st.session_state.filter_dates)}/{len(dates)}</span></div>', unsafe_allow_html=True)
            a, b = st.columns(2)
            a.button("All", key="dates_all", on_click=set_filter, args=("filter_dates", dates), width="stretch")
            b.button("Clear", key="dates_clear", on_click=set_filter, args=("filter_dates", []), width="stretch")
            selected_dates = st.multiselect("Specific Dates", dates, key="filter_dates", label_visibility="collapsed", format_func=lambda d: d.strftime("%d %b %Y"), persist_state="session")

    for label, icon, options, key in [("Farm", "🏠", farms, "filter_farms"), ("Group", "🏷️", groups, "filter_groups"), ("Crop", "🌱", crops, "filter_crops")]:
        with st.container(key=f"filter_card_{label.lower()}"):
            st.markdown(f'<div class="filter-title">{icon} &nbsp;{label}<span class="filter-count">{len(st.session_state[key])}/{len(options)}</span></div>', unsafe_allow_html=True)
            a, b = st.columns(2)
            a.button("All", key=f"{key}_all", on_click=set_filter, args=(key, options), width="stretch")
            b.button("Clear", key=f"{key}_clear", on_click=set_filter, args=(key, []), width="stretch")
            st.multiselect(label, options, key=key, label_visibility="collapsed")

    selected_farms = st.session_state.filter_farms
    selected_groups = st.session_state.filter_groups
    selected_crops = st.session_state.filter_crops
    if date_mode == "Date Range" and len(date_range) == 2:
        sidebar_dates = data["Harvest Date"].dt.date.between(date_range[0], date_range[1])
    elif date_mode == "Specific Dates":
        sidebar_dates = data["Harvest Date"].dt.date.isin(selected_dates)
    else:
        sidebar_dates = data["Harvest Date"].notna() & False
    count = (sidebar_dates & data["Farm"].isin(selected_farms) & data["Group"].isin(selected_groups) & data["Crop"].isin(selected_crops)).sum()
    status.caption(f"Showing {count:,} of {len(data):,} records")

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
    mobile_fig = fig.to_dict()
    mobile_fig["layout"]["yaxis"].update(ticktext=["<br>".join(escape(line) for line in wrap(name, width=16, break_long_words=False, break_on_hyphens=False)) for name in crop_names], tickfont={"size": 9}, title={"standoff": 5})
    mobile_fig["layout"]["margin"] = dict(l=115, r=45, t=30, b=50)
    with st.container(key="desktop_crop_chart"):
        st.plotly_chart(fig, width="stretch", theme=None, key="crop_desktop")
    with st.container(key="mobile_crop_chart"):
        st.plotly_chart(mobile_fig, width="stretch", theme=None, key="crop_mobile")

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
        mobile_fig = fig.to_dict()
        mobile_fig["layout"]["margin"] = dict(l=45, r=45, t=25, b=25)
        with st.container(key="desktop_incentive_chart"):
            st.plotly_chart(fig, width="stretch", theme=None, key="incentive_desktop")
        with st.container(key="mobile_incentive_chart"):
            st.plotly_chart(mobile_fig, width="stretch", theme=None, key="incentive_mobile")
