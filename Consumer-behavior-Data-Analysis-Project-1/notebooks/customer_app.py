import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Shopping Behaviour Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    [data-testid="metric-container"] {
        background: #F8F9FA; border: 1px solid #E9ECEF;
        border-radius: 12px; padding: 16px 20px;
    }
    [data-testid="metric-container"] label {
        font-size: 13px !important; color: #6C757D !important; font-weight: 500 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 26px !important; font-weight: 700 !important; color: #212529 !important;
    }
    [data-testid="stSidebar"] { background: #F8F9FA; border-right: 1px solid #E9ECEF; }
    .section-header {
        font-size: 13px; font-weight: 600; color: #6C757D;
        text-transform: uppercase; letter-spacing: 0.06em; margin: 8px 0 12px 0;
    }
    #MainMenu { visibility: hidden; } footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv("../data/02_processed/customer_data_cleaned.csv")

    # Normalise column names to lowercase_with_underscores
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # -----------------------------------------------------------
    # KEY FIX: your file stores text values with hidden quote
    # characters inside them — e.g. the value 'Winter' contains
    # actual single-quote characters as part of the string.
    # isin(["Winter"]) would never match "'Winter'" so we strip
    # those quote characters from every text column right here.
    # -----------------------------------------------------------
    text_cols = [c for c in df.columns
                 if str(df[c].dtype) in ("object", "string", "str")]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip().str.strip("'\"")

    # Add age_group if not already in file
    if "age_group" not in df.columns:
        df["age_group"] = pd.cut(
            df["age"], bins=[0, 25, 35, 45, 55, 70],
            labels=["18-25", "26-35", "36-45", "46-55", "56-70"]
        )

    # Add frequency_purchase_days if not already in file
    if "frequency_purchase_days" not in df.columns:
        freq_map = {
            "Weekly": 7, "Bi-Weekly": 14, "Fortnightly": 14,
            "Monthly": 30, "Quarterly": 90,
            "Every 3 Months": 90, "Annually": 365
        }
        df["frequency_purchase_days"] = df["frequency_of_purchases"].map(freq_map)

    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error("File not found! Put shopping_dashboard.py and "
             "Customer_shopping_behavior_dataset.xlsx in the same folder.")
    st.stop()

# Detect purchase amount column name
AMT = next(
    (c for c in df.columns if "purchase" in c and "amount" in c),
    None
)
if AMT is None:
    st.error("Could not find purchase amount column."); st.stop()

# Shared chart style
LAYOUT = dict(
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=10, r=10, t=44, b=10), font=dict(size=12)
)
GRID    = dict(showgrid=True, gridcolor="#F2F2F2", gridwidth=0.5)
NO_GRID = dict(showgrid=False)


# ── SIDEBAR ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛍️ Dashboard filters")
    st.markdown("---")

    all_seasons    = sorted(df["season"].dropna().unique().tolist())
    all_genders    = sorted(df["gender"].dropna().unique().tolist())
    all_categories = sorted(df["category"].dropna().unique().tolist())
    all_subs       = sorted(df["subscription_status"].dropna().unique().tolist())
    all_discounts  = sorted(df["discount_applied"].dropna().unique().tolist())

    sel_season   = st.multiselect("Season",              all_seasons,    default=all_seasons)
    sel_gender   = st.multiselect("Gender",              all_genders,    default=all_genders)
    sel_category = st.multiselect("Category",            all_categories, default=all_categories)
    sel_sub      = st.multiselect("Subscription status", all_subs,       default=all_subs)
    sel_discount = st.multiselect("Discount applied",    all_discounts,  default=all_discounts)

    age_range = st.slider(
        "Age range",
        min_value=int(df["age"].min()), max_value=int(df["age"].max()),
        value=(int(df["age"].min()), int(df["age"].max()))
    )
    amount_range = st.slider(
        "Purchase amount (USD)",
        min_value=int(df[AMT].min()), max_value=int(df[AMT].max()),
        value=(int(df[AMT].min()), int(df[AMT].max()))
    )
    st.markdown("---")
    st.caption(f"Total dataset: {len(df):,} customers")


# ── APPLY FILTERS ──────────────────────────────────────────
filtered = df[
    df["season"].isin(sel_season) &
    df["gender"].isin(sel_gender) &
    df["category"].isin(sel_category) &
    df["subscription_status"].isin(sel_sub) &
    df["discount_applied"].isin(sel_discount) &
    df["age"].between(age_range[0], age_range[1]) &
    df[AMT].between(amount_range[0], amount_range[1])
]

if len(filtered) == 0:
    st.warning("No data matches your filters. Please widen your selection.")
    st.stop()


# ── HEADER ─────────────────────────────────────────────────
st.markdown("# 🛍️ Customer Shopping Behaviour Dashboard")
st.markdown(
    f"Showing **{len(filtered):,}** of **{len(df):,}** customers "
    f"&nbsp;·&nbsp; **{len(filtered)/len(df)*100:.0f}%** of total data"
)
st.divider()


# ── KPI CARDS ──────────────────────────────────────────────
st.markdown('<div class="section-header">Key performance indicators</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total revenue",        f"${filtered[AMT].sum():,.0f}",       f"{len(filtered):,} orders")
k2.metric("Avg order value",      f"${filtered[AMT].mean():.2f}")
k3.metric("Avg review rating",    f"⭐ {filtered['review_rating'].mean():.2f}")
k4.metric("Subscription rate",    f"{(filtered['subscription_status']=='Yes').mean()*100:.0f}%")
k5.metric("Avg prev. purchases",  f"{filtered['previous_purchases'].mean():.1f}")
st.divider()


# ── REVENUE BY CATEGORY + SEASON ───────────────────────────
st.markdown('<div class="section-header">Revenue breakdown</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    d = (filtered.groupby("category")[AMT].sum().reset_index()
         .rename(columns={AMT:"revenue"}).sort_values("revenue", ascending=True))
    fig = px.bar(d, x="revenue", y="category", orientation="h",
                 title="Revenue by category", color="revenue",
                 color_continuous_scale=["#BFD7ED","#185FA5"], text="revenue")
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig.update_layout(height=280, coloraxis_showscale=False, **LAYOUT)
    fig.update_xaxes(**GRID); fig.update_yaxes(**NO_GRID)
    st.plotly_chart(fig, width="stretch")

with col2:
    d = (filtered.groupby("season")[AMT].sum().reset_index()
         .rename(columns={AMT:"revenue"}).sort_values("revenue", ascending=False))
    fig = px.bar(d, x="season", y="revenue", title="Revenue by season", color="season",
                 color_discrete_map={"Spring":"#1D9E75","Summer":"#EF9F27",
                                     "Fall":"#D85A30","Winter":"#185FA5"}, text="revenue")
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig.update_layout(height=280, showlegend=False, **LAYOUT)
    fig.update_yaxes(**GRID)
    st.plotly_chart(fig, width="stretch")


# ── TOP ITEMS + AGE GROUP ──────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    d = (filtered.groupby("item_purchased")[AMT].sum().reset_index()
         .rename(columns={AMT:"revenue"}).sort_values("revenue", ascending=False).head(10))
    fig = px.bar(d, x="item_purchased", y="revenue", title="Top 10 items by revenue",
                 color="revenue", color_continuous_scale=["#D9C8F5","#534AB7"], text="revenue")
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig.update_layout(height=340, coloraxis_showscale=False, xaxis_tickangle=-35, **LAYOUT)
    fig.update_yaxes(**GRID)
    st.plotly_chart(fig, width="stretch")

with col4:
    d = (filtered.groupby("age_group", observed=True)[AMT].sum().reset_index()
         .rename(columns={AMT:"revenue"}))
    fig = px.bar(d, x="age_group", y="revenue", title="Revenue by age group",
                 color="revenue", color_continuous_scale=["#FFE5CC","#BA7517"], text="revenue")
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig.update_layout(height=340, coloraxis_showscale=False, **LAYOUT)
    fig.update_yaxes(**GRID)
    st.plotly_chart(fig, width="stretch")

st.divider()


# ── DONUT CHARTS ───────────────────────────────────────────
st.markdown('<div class="section-header">Customer profile breakdown</div>', unsafe_allow_html=True)

def donut(series, title, colors):
    counts = series.value_counts()
    fig = go.Figure(go.Pie(
        labels=counts.index.tolist(), values=counts.values.tolist(),
        hole=0.58, marker_colors=colors, textinfo="percent", textfont_size=12
    ))
    fig.update_layout(title=title, title_font_size=13, height=250,
                      showlegend=True, legend=dict(font=dict(size=11)),
                      margin=dict(l=0,r=0,t=44,b=0), paper_bgcolor="white")
    return fig

d1, d2, d3, d4 = st.columns(4)
d1.plotly_chart(donut(filtered["payment_method"], "Payment methods",
    ["#185FA5","#1D9E75","#BA7517","#534AB7","#D4537E","#D85A30"]), width="stretch")
d2.plotly_chart(donut(filtered["gender"], "Gender split",
    ["#185FA5","#D4537E"]), width="stretch")
d3.plotly_chart(donut(filtered["shipping_type"], "Shipping type",
    ["#1D9E75","#185FA5","#BA7517","#534AB7","#D85A30","#D4537E"]), width="stretch")
d4.plotly_chart(donut(filtered["size"], "Size distribution",
    ["#185FA5","#1D9E75","#BA7517","#534AB7"]), width="stretch")

st.divider()


# ── FREQUENCY + RATING ─────────────────────────────────────
st.markdown('<div class="section-header">Behaviour & satisfaction</div>', unsafe_allow_html=True)
col5, col6 = st.columns(2)

with col5:
    freq_order = ["Weekly","Bi-Weekly","Fortnightly","Monthly",
                  "Quarterly","Every 3 Months","Annually"]
    d = filtered["frequency_of_purchases"].value_counts().reindex(freq_order).reset_index()
    d.columns = ["frequency","count"]
    fig = px.bar(d, x="frequency", y="count", title="Purchase frequency",
                 color="count", color_continuous_scale=["#C8E6C9","#1D9E75"], text="count")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=320, coloraxis_showscale=False, xaxis_tickangle=-25, **LAYOUT)
    fig.update_yaxes(**GRID)
    st.plotly_chart(fig, width="stretch")

with col6:
    fig = px.histogram(filtered, x="review_rating", nbins=20,
                       title="Review rating distribution",
                       color_discrete_sequence=["#EF9F27"])
    fig.update_layout(height=320, bargap=0.08, **LAYOUT)
    fig.update_yaxes(title="Number of customers", **GRID)
    fig.update_xaxes(title="Rating (out of 5.0)", **NO_GRID)
    st.plotly_chart(fig, width="stretch")


# ── FREQUENCY PURCHASE DAYS ────────────────────────────────
col7, col8 = st.columns(2)

with col7:
    fig = px.box(filtered, x="category", y="frequency_purchase_days", color="category",
                 title="Purchase cycle (days) by category",
                 color_discrete_map={"Clothing":"#185FA5","Accessories":"#1D9E75",
                                     "Footwear":"#BA7517","Outerwear":"#D85A30"})
    fig.update_layout(height=320, showlegend=False, **LAYOUT)
    fig.update_yaxes(title="Days between purchases", **GRID)
    st.plotly_chart(fig, width="stretch")

with col8:
    d = (filtered.groupby(["gender","category"])["frequency_purchase_days"]
         .mean().round(1).reset_index()
         .rename(columns={"frequency_purchase_days":"avg_days"}))
    fig = px.bar(d, x="category", y="avg_days", color="gender", barmode="group",
                 title="Avg purchase cycle (days) — gender vs category",
                 color_discrete_map={"Male":"#185FA5","Female":"#D4537E"}, text="avg_days")
    fig.update_traces(texttemplate="%{text:.0f}d", textposition="outside")
    fig.update_layout(height=320, **LAYOUT)
    fig.update_yaxes(title="Avg days", **GRID)
    st.plotly_chart(fig, width="stretch")

st.divider()


# ── SCATTER ────────────────────────────────────────────────
st.markdown('<div class="section-header">Age vs spending patterns</div>', unsafe_allow_html=True)
fig = px.scatter(filtered, x="age", y=AMT, color="category",
                 size="previous_purchases",
                 hover_data=["item_purchased","gender","season","frequency_purchase_days"],
                 title="Age vs purchase amount — dot size = previous purchases",
                 color_discrete_map={"Clothing":"#185FA5","Accessories":"#1D9E75",
                                     "Footwear":"#BA7517","Outerwear":"#D85A30"},
                 opacity=0.65)
fig.update_layout(height=420, **LAYOUT)
fig.update_xaxes(title="Customer age", **GRID)
fig.update_yaxes(title="Purchase amount (USD)", **GRID)
st.plotly_chart(fig, width="stretch")
st.divider()


# ── DISCOUNT / PROMO / SUBSCRIPTION ────────────────────────
st.markdown('<div class="section-header">Discount, promo & subscription</div>', unsafe_allow_html=True)
dc1, dc2, dc3 = st.columns(3)

with dc1:
    d = (filtered.groupby("discount_applied")[AMT].mean()
         .reset_index().rename(columns={AMT:"avg_spend"}))
    fig = px.bar(d, x="discount_applied", y="avg_spend",
                 title="Avg spend — discount applied?", color="discount_applied",
                 color_discrete_map={"Yes":"#1D9E75","No":"#ADB5BD"}, text="avg_spend")
    fig.update_traces(texttemplate="$%{text:.2f}", textposition="outside")
    fig.update_layout(height=300, showlegend=False, **LAYOUT); fig.update_yaxes(**GRID)
    st.plotly_chart(fig, width="stretch")

with dc2:
    promo_col = "promo_code_used" if "promo_code_used" in df.columns else "discount_applied"
    d = filtered.groupby(promo_col)["review_rating"].mean().reset_index()
    fig = px.bar(d, x=promo_col, y="review_rating",
                 title="Avg rating — promo code used?", color=promo_col,
                 color_discrete_map={"Yes":"#534AB7","No":"#ADB5BD"}, text="review_rating")
    fig.update_traces(texttemplate="%{text:.2f} ★", textposition="outside")
    fig.update_layout(height=300, showlegend=False, yaxis_range=[0,5.2], **LAYOUT)
    fig.update_yaxes(**GRID)
    st.plotly_chart(fig, width="stretch")

with dc3:
    d = (filtered.groupby("subscription_status")[AMT].mean()
         .reset_index().rename(columns={AMT:"avg_spend"}))
    fig = px.bar(d, x="subscription_status", y="avg_spend",
                 title="Avg spend — subscribed?", color="subscription_status",
                 color_discrete_map={"Yes":"#D85A30","No":"#ADB5BD"}, text="avg_spend")
    fig.update_traces(texttemplate="$%{text:.2f}", textposition="outside")
    fig.update_layout(height=300, showlegend=False, **LAYOUT); fig.update_yaxes(**GRID)
    st.plotly_chart(fig, width="stretch")

st.divider()


# ── TOP 15 LOCATIONS ───────────────────────────────────────
st.markdown('<div class="section-header">Top locations by revenue</div>', unsafe_allow_html=True)
d = (filtered.groupby("location")[AMT].sum().reset_index()
     .rename(columns={AMT:"revenue"}).sort_values("revenue", ascending=False).head(15))
fig = px.bar(d, x="location", y="revenue", title="Top 15 locations by total revenue",
             color="revenue", color_continuous_scale=["#BFD7ED","#185FA5"], text="revenue")
fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
fig.update_layout(height=340, coloraxis_showscale=False, xaxis_tickangle=-35, **LAYOUT)
fig.update_yaxes(**GRID)
st.plotly_chart(fig, width="stretch")
st.divider()


# ── RAW DATA + DOWNLOAD ────────────────────────────────────
with st.expander("📋 View & download filtered data"):
    st.write(f"**{len(filtered):,} rows** match your current filters")
    st.dataframe(filtered.reset_index(drop=True), width="stretch", height=400)
    st.download_button(
        label="⬇️ Download as CSV",
        data=filtered.to_csv(index=False),
        file_name="filtered_shopping_data.csv",
        mime="text/csv"
    )

st.markdown(
    "<div style='text-align:center;color:#ADB5BD;font-size:12px;padding:20px 0 10px'>"
    "Built with Python &nbsp;·&nbsp; Streamlit &nbsp;·&nbsp; Plotly &nbsp;·&nbsp; Pandas"
    "</div>", unsafe_allow_html=True
)