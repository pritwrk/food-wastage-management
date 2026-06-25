import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FoodBridge — Wastage Management",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide default streamlit elements */
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f1117;
    border-right: 1px solid #1e2130;
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

/* Sidebar brand */
.sidebar-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #4ade80;
    padding: 0 1rem 1.5rem 1rem;
    border-bottom: 1px solid #1e2130;
    margin-bottom: 1.5rem;
    letter-spacing: -0.3px;
}
.sidebar-brand span {
    color: #fff;
}

/* Nav items */
.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 16px;
    border-radius: 8px;
    margin-bottom: 4px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    color: #8b92a5;
    transition: all 0.15s;
}
.nav-item:hover { background: #1a1f2e; color: #fff; }
.nav-item.active { background: #162032; color: #4ade80; }

/* Page header */
.page-header {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #1e2130;
}
.page-header h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0;
    letter-spacing: -0.5px;
}
.page-header p {
    color: #64748b;
    font-size: 0.875rem;
    margin: 4px 0 0 0;
}

/* KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: #0f1117;
    border: 1px solid #1e2130;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
}
.kpi-card.green::before { background: #4ade80; }
.kpi-card.blue::before  { background: #60a5fa; }
.kpi-card.purple::before{ background: #a78bfa; }
.kpi-card.orange::before{ background: #fb923c; }

.kpi-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 8px;
}
.kpi-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1;
}
.kpi-icon {
    position: absolute;
    right: 1.25rem;
    top: 1.25rem;
    font-size: 1.5rem;
    opacity: 0.3;
}

/* Section card */
.section-card {
    background: #0f1117;
    border: 1px solid #1e2130;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #cbd5e1;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Table styling */
.dataframe { font-size: 0.85rem !important; }

/* Selectbox & inputs */
.stSelectbox label, .stTextInput label, .stNumberInput label, .stDateInput label {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
}
.badge-green { background: #052e16; color: #4ade80; }
.badge-blue  { background: #0c1a2e; color: #60a5fa; }

/* Success / error */
.stSuccess, .stError { border-radius: 8px !important; }

/* Radio buttons */
.stRadio label { font-size: 0.875rem !important; }

/* Divider */
.custom-divider {
    height: 1px;
    background: #1e2130;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── DB Connection ─────────────────────────────────────────────────────────────
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=int(st.secrets["DB_PORT"]),
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        use_pure=True
    )

def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ── Chart theme ───────────────────────────────────────────────────────────────
CHART_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor":  "rgba(0,0,0,0)",
    "font_color":    "#94a3b8",
    "font_family":   "Inter",
}
COLORS = ["#4ade80", "#60a5fa", "#a78bfa", "#fb923c", "#f472b6", "#34d399"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🍱 Food<span>Bridge</span></div>', unsafe_allow_html=True)
    menu = st.radio(
        "Navigation",
        ["📊  Dashboard", "🔍  SQL Queries", "🥗  Food Listings",
         "🏪  Providers", "🤝  Receivers", "✏️  Manage Data"],
        label_visibility="collapsed"
    )
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#374151;font-size:0.7rem;padding:0 0.5rem;">LOCAL FOOD WASTAGE MANAGEMENT SYSTEM v1.0</div>', unsafe_allow_html=True)

# ── Strip emoji prefix ────────────────────────────────────────────────────────
page = menu.split("  ")[-1]

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown("""
    <div class="page-header">
        <h1>Dashboard</h1>
        <p>Real-time overview of food distribution activity</p>
    </div>""", unsafe_allow_html=True)

    # KPI
    p = run_query("SELECT COUNT(*) as c FROM providers")["c"][0]
    r = run_query("SELECT COUNT(*) as c FROM receivers")["c"][0]
    f = run_query("SELECT COUNT(*) as c FROM food_listings")["c"][0]
    c = run_query("SELECT COUNT(*) as c FROM claims")["c"][0]

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card green">
            <div class="kpi-icon">🏪</div>
            <div class="kpi-label">Providers</div>
            <div class="kpi-value">{p}</div>
        </div>
        <div class="kpi-card blue">
            <div class="kpi-icon">🤝</div>
            <div class="kpi-label">Receivers</div>
            <div class="kpi-value">{r}</div>
        </div>
        <div class="kpi-card purple">
            <div class="kpi-icon">🥗</div>
            <div class="kpi-label">Food Listings</div>
            <div class="kpi-value">{f}</div>
        </div>
        <div class="kpi-card orange">
            <div class="kpi-icon">📋</div>
            <div class="kpi-label">Total Claims</div>
            <div class="kpi-value">{c}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Charts row 1
    col1, col2 = st.columns(2)

    with col1:
        df_status = run_query("SELECT Status, COUNT(*) as count FROM claims GROUP BY Status")
        fig = px.pie(df_status, names="Status", values="count",
                     hole=0.55,
                     color="Status",
                     color_discrete_map={"Completed": "#4ade80", "Pending": "#fb923c", "Cancelled": "#f87171"})
        fig.update_layout(**CHART_THEME, title=dict(text="Claims Status", font_color="#cbd5e1", font_size=14),
                          legend=dict(orientation="h", y=-0.1),
                          margin=dict(t=50, b=30, l=0, r=0))
        fig.update_traces(textfont_color="#fff")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_ftype = run_query("SELECT Food_Type, COUNT(*) as count FROM food_listings GROUP BY Food_Type ORDER BY count DESC")
        fig2 = px.bar(df_ftype, x="Food_Type", y="count",
                      color="Food_Type",
                      color_discrete_sequence=COLORS,
                      text="count")
        fig2.update_layout(**CHART_THEME, title=dict(text="Food Type Distribution", font_color="#cbd5e1", font_size=14),
                           showlegend=False,
                           xaxis=dict(gridcolor="#1e2130"),
                           yaxis=dict(gridcolor="#1e2130"),
                           margin=dict(t=50, b=10, l=0, r=0))
        fig2.update_traces(textposition="outside", textfont_color="#94a3b8")
        st.plotly_chart(fig2, use_container_width=True)

    # Chart row 2
    col3, col4 = st.columns(2)

    with col3:
        df_ptype = run_query("""SELECT p.Type, SUM(fl.Quantity) as total
                                FROM providers p JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID
                                GROUP BY p.Type ORDER BY total DESC""")
        fig3 = px.bar(df_ptype, x="total", y="Type", orientation="h",
                      color="Type", color_discrete_sequence=COLORS, text="total")
        fig3.update_layout(**CHART_THEME, title=dict(text="Quantity by Provider Type", font_color="#cbd5e1", font_size=14),
                           showlegend=False,
                           xaxis=dict(gridcolor="#1e2130"),
                           yaxis=dict(gridcolor="#1e2130"),
                           margin=dict(t=50, b=10, l=0, r=0))
        fig3.update_traces(textposition="outside", textfont_color="#94a3b8")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        df_meal = run_query("""SELECT fl.Meal_Type, COUNT(c.Claim_ID) as claims
                               FROM food_listings fl JOIN claims c ON fl.Food_ID = c.Food_ID
                               GROUP BY fl.Meal_Type ORDER BY claims DESC""")
        fig4 = px.pie(df_meal, names="Meal_Type", values="claims",
                      hole=0.55, color_discrete_sequence=COLORS)
        fig4.update_layout(**CHART_THEME, title=dict(text="Claims by Meal Type", font_color="#cbd5e1", font_size=14),
                           legend=dict(orientation="h", y=-0.1),
                           margin=dict(t=50, b=30, l=0, r=0))
        fig4.update_traces(textfont_color="#fff")
        st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SQL QUERIES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "SQL Queries":
    st.markdown("""
    <div class="page-header">
        <h1>SQL Queries</h1>
        <p>15 business intelligence queries — select and explore</p>
    </div>""", unsafe_allow_html=True)

    queries = {
        "01 · Providers per City":            "SELECT City, COUNT(*) as total_providers FROM providers GROUP BY City ORDER BY total_providers DESC",
        "02 · Provider Type Contribution":    "SELECT Type, COUNT(*) as total FROM providers GROUP BY Type ORDER BY total DESC",
        "03 · Top 10 Receivers by Claims":    "SELECT r.Name, r.Type, COUNT(c.Claim_ID) as total_claims FROM receivers r JOIN claims c ON r.Receiver_ID = c.Receiver_ID GROUP BY r.Receiver_ID, r.Name, r.Type ORDER BY total_claims DESC LIMIT 10",
        "04 · Total Food Quantity":           "SELECT SUM(Quantity) as total_quantity FROM food_listings",
        "05 · City with Most Listings":       "SELECT Location, COUNT(*) as total_listings FROM food_listings GROUP BY Location ORDER BY total_listings DESC",
        "06 · Common Food Types":             "SELECT Food_Type, COUNT(*) as count FROM food_listings GROUP BY Food_Type ORDER BY count DESC",
        "07 · Claims per Food Item":          "SELECT fl.Food_Name, COUNT(c.Claim_ID) as total_claims FROM food_listings fl JOIN claims c ON fl.Food_ID = c.Food_ID GROUP BY fl.Food_ID, fl.Food_Name ORDER BY total_claims DESC LIMIT 10",
        "08 · Top Providers by Success":      "SELECT p.Name, p.Type, COUNT(c.Claim_ID) as successful_claims FROM providers p JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID JOIN claims c ON fl.Food_ID = c.Food_ID WHERE c.Status = 'Completed' GROUP BY p.Provider_ID, p.Name, p.Type ORDER BY successful_claims DESC LIMIT 10",
        "09 · Claims Status %":               "SELECT Status, COUNT(*) as count, ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) as percentage FROM claims GROUP BY Status",
        "10 · Avg Quantity per Claim":        "SELECT ROUND(AVG(fl.Quantity), 2) as avg_quantity FROM claims c JOIN food_listings fl ON c.Food_ID = fl.Food_ID WHERE c.Status = 'Completed'",
        "11 · Most Claimed Meal Type":        "SELECT fl.Meal_Type, COUNT(c.Claim_ID) as total_claims FROM food_listings fl JOIN claims c ON fl.Food_ID = c.Food_ID GROUP BY fl.Meal_Type ORDER BY total_claims DESC",
        "12 · Total Donated per Provider":    "SELECT p.Name, SUM(fl.Quantity) as total_donated FROM providers p JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID GROUP BY p.Provider_ID, p.Name ORDER BY total_donated DESC LIMIT 10",
        "13 · City-wise Claim Success Rate":  "SELECT fl.Location, COUNT(c.Claim_ID) as total_claims, ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate FROM food_listings fl JOIN claims c ON fl.Food_ID = c.Food_ID GROUP BY fl.Location ORDER BY success_rate DESC",
        "14 · Receivers per City":            "SELECT City, COUNT(*) as total_receivers FROM receivers GROUP BY City ORDER BY total_receivers DESC",
        "15 · Claims by Provider Type":       "SELECT p.Type, COUNT(c.Claim_ID) as total_claims FROM providers p JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID JOIN claims c ON fl.Food_ID = c.Food_ID GROUP BY p.Type ORDER BY total_claims DESC",
    }

    selected = st.selectbox("Select a query", list(queries.keys()))
    df = run_query(queries[selected])

    col_info, col_rows = st.columns([3,1])
    with col_rows:
        st.markdown(f'<div style="text-align:right;color:#64748b;font-size:0.8rem;padding-top:0.3rem;">{len(df)} rows returned</div>', unsafe_allow_html=True)

    st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# FOOD LISTINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Food Listings":
    st.markdown("""
    <div class="page-header">
        <h1>Food Listings</h1>
        <p>Browse and filter available food by city, type, and meal</p>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    cities     = ["All"] + list(run_query("SELECT DISTINCT Location FROM food_listings ORDER BY Location")["Location"])
    food_types = ["All"] + list(run_query("SELECT DISTINCT Food_Type FROM food_listings")["Food_Type"])
    meal_types = ["All"] + list(run_query("SELECT DISTINCT Meal_Type FROM food_listings")["Meal_Type"])

    city      = col1.selectbox("City", cities)
    food_type = col2.selectbox("Food Type", food_types)
    meal_type = col3.selectbox("Meal Type", meal_types)

    query = """SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Expiry_Date,
                      fl.Food_Type, fl.Meal_Type, fl.Location,
                      p.Name as Provider, p.Contact
               FROM food_listings fl
               JOIN providers p ON fl.Provider_ID = p.Provider_ID
               WHERE 1=1"""
    if city      != "All": query += f" AND fl.Location = '{city}'"
    if food_type != "All": query += f" AND fl.Food_Type = '{food_type}'"
    if meal_type != "All": query += f" AND fl.Meal_Type = '{meal_type}'"

    df = run_query(query)
    st.markdown(f'<div style="color:#64748b;font-size:0.8rem;margin-bottom:0.5rem;">{len(df)} listings found</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PROVIDERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Providers":
    st.markdown("""
    <div class="page-header">
        <h1>Providers</h1>
        <p>Directory of food providers — restaurants, supermarkets, grocery stores</p>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    cities = ["All"] + list(run_query("SELECT DISTINCT City FROM providers ORDER BY City")["City"])
    types  = ["All"] + list(run_query("SELECT DISTINCT Type FROM providers ORDER BY Type")["Type"])
    city   = col1.selectbox("City", cities)
    ptype  = col2.selectbox("Type", types)

    query = "SELECT Name, Type, City, Contact FROM providers WHERE 1=1"
    if city  != "All": query += f" AND City = '{city}'"
    if ptype != "All": query += f" AND Type = '{ptype}'"

    df = run_query(query)
    st.markdown(f'<div style="color:#64748b;font-size:0.8rem;margin-bottom:0.5rem;">{len(df)} providers found</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# RECEIVERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Receivers":
    st.markdown("""
    <div class="page-header">
        <h1>Receivers</h1>
        <p>Directory of receivers — NGOs, shelters, individuals</p>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    cities = ["All"] + list(run_query("SELECT DISTINCT City FROM receivers ORDER BY City")["City"])
    types  = ["All"] + list(run_query("SELECT DISTINCT Type FROM receivers ORDER BY Type")["Type"])
    city   = col1.selectbox("City", cities)
    rtype  = col2.selectbox("Type", types)

    query = "SELECT Name, Type, City, Contact FROM receivers WHERE 1=1"
    if city  != "All": query += f" AND City = '{city}'"
    if rtype != "All": query += f" AND Type = '{rtype}'"

    df = run_query(query)
    st.markdown(f'<div style="color:#64748b;font-size:0.8rem;margin-bottom:0.5rem;">{len(df)} receivers found</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# MANAGE DATA (CRUD)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Manage Data":
    st.markdown("""
    <div class="page-header">
        <h1>Manage Data</h1>
        <p>Add, update, or remove food listings from the system</p>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["➕  Add Listing", "✏️  Update Listing", "🗑️  Delete Listing"])

    with tab1:
        with st.form("add_food", clear_on_submit=True):
            col1, col2 = st.columns(2)
            food_name   = col1.text_input("Food Name")
            quantity    = col2.number_input("Quantity", min_value=1)
            col3, col4  = st.columns(2)
            expiry      = col3.date_input("Expiry Date")
            provider_id = col4.number_input("Provider ID", min_value=1)
            col5, col6  = st.columns(2)
            food_type   = col5.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            meal_type   = col6.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
            location    = st.text_input("Location")
            submitted   = st.form_submit_button("Add Food Listing", use_container_width=True)

            if submitted:
                if food_name and location:
                    conn   = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO food_listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Location, Food_Type, Meal_Type) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (food_name, quantity, expiry, provider_id, location, food_type, meal_type)
                    )
                    conn.commit(); conn.close()
                    st.success(f"✅ '{food_name}' added successfully!")
                else:
                    st.error("Food Name and Location are required.")

    with tab2:
        food_id = st.number_input("Food ID to update", min_value=1, key="upd_id")
        with st.form("update_food"):
            col1, col2 = st.columns(2)
            new_qty    = col1.number_input("New Quantity", min_value=1)
            new_expiry = col2.date_input("New Expiry Date")
            new_ftype  = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            submitted  = st.form_submit_button("Update Listing", use_container_width=True)
            if submitted:
                conn   = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE food_listings SET Quantity=%s, Expiry_Date=%s, Food_Type=%s WHERE Food_ID=%s",
                    (new_qty, new_expiry, new_ftype, food_id)
                )
                conn.commit()
                rows = cursor.rowcount
                conn.close()
                if rows == 0: st.error(f"Food ID {food_id} not found.")
                else: st.success(f"✅ Food ID {food_id} updated successfully!")

    with tab3:
        st.warning("⚠️ This action is permanent and cannot be undone.")
        food_id = st.number_input("Food ID to delete", min_value=1, key="del_id")
        if st.button("Delete Listing", type="primary", use_container_width=True):
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM food_listings WHERE Food_ID=%s", (food_id,))
            conn.commit()
            rows = cursor.rowcount
            conn.close()
            if rows == 0: st.error(f"Food ID {food_id} not found.")
            else: st.success(f"✅ Food ID {food_id} deleted successfully!")
