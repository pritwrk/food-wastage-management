import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FoodBridge — Wastage Management",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* App background */
.stApp { background: #0d1117; }
.block-container { padding-top: 1.75rem; padding-bottom: 2rem; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #1f2937;
}

.brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: -0.3px;
    padding: 0 0.5rem 1.25rem;
    border-bottom: 1px solid #1f2937;
    margin-bottom: 1.25rem;
}
.brand-food { color: #4ade80; }
.brand-bridge { color: #f1f5f9; }
.brand-tag {
    font-size: 0.65rem;
    font-weight: 500;
    color: #4b5563;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 2px;
}

.divider { height: 1px; background: #1f2937; margin: 1rem 0; }

.sidebar-links {
    font-size: 0.75rem;
    color: #6b7280;
    line-height: 2;
    padding: 0 0.5rem;
}
.sidebar-links a {
    color: #4ade80;
    text-decoration: none;
    font-weight: 500;
}
.sidebar-links a:hover { text-decoration: underline; }
.sidebar-version {
    font-size: 0.65rem;
    color: #374151;
    margin-top: 0.75rem;
    padding: 0 0.5rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── Page header ── */
.page-header {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #1f2937;
}
.page-header h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
    color: #f9fafb;
    margin: 0;
    letter-spacing: -0.4px;
}
.page-header p {
    color: #6b7280;
    font-size: 0.85rem;
    margin: 5px 0 0 0;
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.75rem;
}
.kpi-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 10px 10px 0 0;
}
.kpi-green::after  { background: linear-gradient(90deg, #4ade80, #22c55e); }
.kpi-blue::after   { background: linear-gradient(90deg, #60a5fa, #3b82f6); }
.kpi-purple::after { background: linear-gradient(90deg, #c084fc, #a855f7); }
.kpi-amber::after  { background: linear-gradient(90deg, #fbbf24, #f59e0b); }

.kpi-icon { font-size: 1.4rem; opacity: 0.2; position: absolute; right: 1.1rem; top: 1.1rem; }
.kpi-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: #4b5563;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 6px;
}
.kpi-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #f9fafb;
    line-height: 1;
}

/* ── Row count ── */
.row-count {
    font-size: 0.78rem;
    color: #4b5563;
    margin-bottom: 0.5rem;
}

/* ── Input labels ── */
.stSelectbox label, .stTextInput label,
.stNumberInput label, .stDateInput label {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #6b7280 !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

/* ── Radio nav ── */
.stRadio > div { gap: 2px; }
.stRadio label {
    font-size: 0.85rem !important;
    color: #9ca3af !important;
    padding: 6px 10px;
    border-radius: 6px;
}
.stRadio label:hover { color: #f1f5f9 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] { font-size: 0.875rem; font-weight: 500; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── DB ────────────────────────────────────────────────────────────────────────
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=int(st.secrets["DB_PORT"]),
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        use_pure=True
    )

def run_query(q):
    conn = get_connection()
    df = pd.read_sql(q, conn)
    conn.close()
    return df

# ── Chart config ──────────────────────────────────────────────────────────────
CT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#111827",
          font_color="#9ca3af", font_family="Inter")
GRID = dict(gridcolor="#1f2937", linecolor="#1f2937", zerolinecolor="#1f2937")
C = ["#4ade80","#60a5fa","#c084fc","#fbbf24","#f472b6","#34d399","#38bdf8"]

def dark_chart(fig, title):
    fig.update_layout(**CT,
        title=dict(text=title, font_color="#e5e7eb", font_size=13, font_family="Space Grotesk"),
        margin=dict(t=48, b=12, l=0, r=0),
        legend=dict(font_color="#9ca3af")
    )
    return fig

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div><span class="brand-food">Food</span><span class="brand-bridge">Bridge</span> 🍱</div>
        <div class="brand-tag">Wastage Management System</div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio("nav", [
        "📊  Dashboard", "🔍  SQL Queries", "🥗  Food Listings",
        "🏪  Providers", "🤝  Receivers", "✏️  Manage Data"
    ], label_visibility="collapsed")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-links">
        <div><b style="color:#9ca3af;">🔗 Project Links</b></div>
        <div>📁 <a href="https://github.com/pritwrk/food-wastage-management" target="_blank">GitHub Repository</a></div>
        <div>👤 <a href="https://github.com/pritwrk" target="_blank">github.com/pritwrk</a></div>
    </div>
    <div class="sidebar-version">v1.0 · Local Food Wastage Mgmt</div>
    """, unsafe_allow_html=True)

page = menu.split("  ")[-1]

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown("""<div class="page-header">
        <h1>Dashboard</h1>
        <p>Real-time overview of food distribution activity</p>
    </div>""", unsafe_allow_html=True)

    p = run_query("SELECT COUNT(*) as c FROM providers")["c"][0]
    r = run_query("SELECT COUNT(*) as c FROM receivers")["c"][0]
    f = run_query("SELECT COUNT(*) as c FROM food_listings")["c"][0]
    c = run_query("SELECT COUNT(*) as c FROM claims")["c"][0]

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card kpi-green">
        <div class="kpi-icon">🏪</div>
        <div class="kpi-label">Total Providers</div>
        <div class="kpi-value">{p:,}</div>
      </div>
      <div class="kpi-card kpi-blue">
        <div class="kpi-icon">🤝</div>
        <div class="kpi-label">Total Receivers</div>
        <div class="kpi-value">{r:,}</div>
      </div>
      <div class="kpi-card kpi-purple">
        <div class="kpi-icon">🥗</div>
        <div class="kpi-label">Food Listings</div>
        <div class="kpi-value">{f:,}</div>
      </div>
      <div class="kpi-card kpi-amber">
        <div class="kpi-icon">📋</div>
        <div class="kpi-label">Total Claims</div>
        <div class="kpi-value">{c:,}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        df = run_query("SELECT Status, COUNT(*) as count FROM claims GROUP BY Status")
        fig = px.pie(df, names="Status", values="count", hole=0.58,
                     color="Status",
                     color_discrete_map={"Completed":"#4ade80","Pending":"#fbbf24","Cancelled":"#f87171"})
        fig.update_traces(textfont_color="#fff", textfont_size=12)
        fig.update_layout(**CT,
            title=dict(text="Claims Status Distribution", font_color="#e5e7eb", font_size=13),
            legend=dict(orientation="h", y=-0.15, font_color="#9ca3af"),
            margin=dict(t=48,b=40,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        df = run_query("SELECT Food_Type, COUNT(*) as count FROM food_listings GROUP BY Food_Type ORDER BY count DESC")
        fig = px.bar(df, x="Food_Type", y="count", color="Food_Type",
                     color_discrete_sequence=C, text="count")
        fig.update_traces(textposition="outside", textfont_color="#9ca3af", marker_line_width=0)
        fig.update_layout(**CT,
            title=dict(text="Food Type Distribution", font_color="#e5e7eb", font_size=13),
            xaxis=dict(**GRID, title=""), yaxis=dict(**GRID, title=""),
            showlegend=False, margin=dict(t=48,b=10,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        df = run_query("""SELECT p.Type, SUM(fl.Quantity) as total
            FROM providers p JOIN food_listings fl ON p.Provider_ID=fl.Provider_ID
            GROUP BY p.Type ORDER BY total DESC""")
        fig = px.bar(df, x="total", y="Type", orientation="h",
                     color="Type", color_discrete_sequence=C, text="total")
        fig.update_traces(textposition="outside", textfont_color="#9ca3af", marker_line_width=0)
        fig.update_layout(**CT,
            title=dict(text="Food Quantity by Provider Type", font_color="#e5e7eb", font_size=13),
            xaxis=dict(**GRID, title=""), yaxis=dict(**GRID, title=""),
            showlegend=False, margin=dict(t=48,b=10,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        df = run_query("""SELECT fl.Meal_Type, COUNT(c.Claim_ID) as claims
            FROM food_listings fl JOIN claims c ON fl.Food_ID=c.Food_ID
            GROUP BY fl.Meal_Type ORDER BY claims DESC""")
        fig = px.pie(df, names="Meal_Type", values="claims",
                     hole=0.58, color_discrete_sequence=C)
        fig.update_traces(textfont_color="#fff", textfont_size=12)
        fig.update_layout(**CT,
            title=dict(text="Claims by Meal Type", font_color="#e5e7eb", font_size=13),
            legend=dict(orientation="h", y=-0.15, font_color="#9ca3af"),
            margin=dict(t=48,b=40,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SQL QUERIES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "SQL Queries":
    st.markdown("""<div class="page-header">
        <h1>SQL Queries</h1>
        <p>15 business intelligence queries — select and explore results</p>
    </div>""", unsafe_allow_html=True)

    queries = {
        "01 · Providers per City":           "SELECT City, COUNT(*) as total_providers FROM providers GROUP BY City ORDER BY total_providers DESC",
        "02 · Provider Type Contribution":   "SELECT Type, COUNT(*) as total FROM providers GROUP BY Type ORDER BY total DESC",
        "03 · Top 10 Receivers by Claims":   "SELECT r.Name, r.Type, COUNT(c.Claim_ID) as total_claims FROM receivers r JOIN claims c ON r.Receiver_ID=c.Receiver_ID GROUP BY r.Receiver_ID, r.Name, r.Type ORDER BY total_claims DESC LIMIT 10",
        "04 · Total Food Quantity":          "SELECT SUM(Quantity) as total_quantity FROM food_listings",
        "05 · City with Most Listings":      "SELECT Location, COUNT(*) as total_listings FROM food_listings GROUP BY Location ORDER BY total_listings DESC",
        "06 · Common Food Types":            "SELECT Food_Type, COUNT(*) as count FROM food_listings GROUP BY Food_Type ORDER BY count DESC",
        "07 · Claims per Food Item":         "SELECT fl.Food_Name, COUNT(c.Claim_ID) as total_claims FROM food_listings fl JOIN claims c ON fl.Food_ID=c.Food_ID GROUP BY fl.Food_ID, fl.Food_Name ORDER BY total_claims DESC LIMIT 10",
        "08 · Top Providers by Success":     "SELECT p.Name, p.Type, COUNT(c.Claim_ID) as successful_claims FROM providers p JOIN food_listings fl ON p.Provider_ID=fl.Provider_ID JOIN claims c ON fl.Food_ID=c.Food_ID WHERE c.Status='Completed' GROUP BY p.Provider_ID, p.Name, p.Type ORDER BY successful_claims DESC LIMIT 10",
        "09 · Claims Status %":              "SELECT Status, COUNT(*) as count, ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM claims),2) as percentage FROM claims GROUP BY Status",
        "10 · Avg Quantity per Claim":       "SELECT ROUND(AVG(fl.Quantity),2) as avg_quantity FROM claims c JOIN food_listings fl ON c.Food_ID=fl.Food_ID WHERE c.Status='Completed'",
        "11 · Most Claimed Meal Type":       "SELECT fl.Meal_Type, COUNT(c.Claim_ID) as total_claims FROM food_listings fl JOIN claims c ON fl.Food_ID=c.Food_ID GROUP BY fl.Meal_Type ORDER BY total_claims DESC",
        "12 · Total Donated per Provider":   "SELECT p.Name, SUM(fl.Quantity) as total_donated FROM providers p JOIN food_listings fl ON p.Provider_ID=fl.Provider_ID GROUP BY p.Provider_ID, p.Name ORDER BY total_donated DESC LIMIT 10",
        "13 · City-wise Claim Success Rate": "SELECT fl.Location, COUNT(c.Claim_ID) as total_claims, ROUND(SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) as success_rate FROM food_listings fl JOIN claims c ON fl.Food_ID=c.Food_ID GROUP BY fl.Location ORDER BY success_rate DESC",
        "14 · Receivers per City":           "SELECT City, COUNT(*) as total_receivers FROM receivers GROUP BY City ORDER BY total_receivers DESC",
        "15 · Claims by Provider Type":      "SELECT p.Type, COUNT(c.Claim_ID) as total_claims FROM providers p JOIN food_listings fl ON p.Provider_ID=fl.Provider_ID JOIN claims c ON fl.Food_ID=c.Food_ID GROUP BY p.Type ORDER BY total_claims DESC",
    }

    selected = st.selectbox("Select a query", list(queries.keys()))
    df = run_query(queries[selected])
    ca, cb = st.columns([4,1])
    with cb: st.markdown(f'<div class="row-count" style="text-align:right">{len(df)} rows</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# FOOD LISTINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Food Listings":
    st.markdown("""<div class="page-header">
        <h1>Food Listings</h1>
        <p>Browse and filter available food by city, type, and meal</p>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    cities     = ["All"] + list(run_query("SELECT DISTINCT Location FROM food_listings ORDER BY Location")["Location"])
    food_types = ["All"] + list(run_query("SELECT DISTINCT Food_Type FROM food_listings")["Food_Type"])
    meal_types = ["All"] + list(run_query("SELECT DISTINCT Meal_Type FROM food_listings")["Meal_Type"])
    city      = c1.selectbox("City", cities)
    food_type = c2.selectbox("Food Type", food_types)
    meal_type = c3.selectbox("Meal Type", meal_types)

    q = """SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Expiry_Date,
                  fl.Food_Type, fl.Meal_Type, fl.Location,
                  p.Name as Provider, p.Contact
           FROM food_listings fl JOIN providers p ON fl.Provider_ID=p.Provider_ID WHERE 1=1"""
    if city      != "All": q += f" AND fl.Location='{city}'"
    if food_type != "All": q += f" AND fl.Food_Type='{food_type}'"
    if meal_type != "All": q += f" AND fl.Meal_Type='{meal_type}'"
    df = run_query(q)
    st.markdown(f'<div class="row-count">{len(df)} listings found</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PROVIDERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Providers":
    st.markdown("""<div class="page-header">
        <h1>Providers</h1>
        <p>Restaurants, supermarkets, grocery stores & catering services</p>
    </div>""", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    cities = ["All"] + list(run_query("SELECT DISTINCT City FROM providers ORDER BY City")["City"])
    types  = ["All"] + list(run_query("SELECT DISTINCT Type FROM providers ORDER BY Type")["Type"])
    city  = c1.selectbox("City", cities)
    ptype = c2.selectbox("Type", types)
    q = "SELECT Name, Type, City, Contact FROM providers WHERE 1=1"
    if city  != "All": q += f" AND City='{city}'"
    if ptype != "All": q += f" AND Type='{ptype}'"
    df = run_query(q)
    st.markdown(f'<div class="row-count">{len(df)} providers found</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# RECEIVERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Receivers":
    st.markdown("""<div class="page-header">
        <h1>Receivers</h1>
        <p>NGOs, shelters, charities & individuals</p>
    </div>""", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    cities = ["All"] + list(run_query("SELECT DISTINCT City FROM receivers ORDER BY City")["City"])
    types  = ["All"] + list(run_query("SELECT DISTINCT Type FROM receivers ORDER BY Type")["Type"])
    city  = c1.selectbox("City", cities)
    rtype = c2.selectbox("Type", types)
    q = "SELECT Name, Type, City, Contact FROM receivers WHERE 1=1"
    if city  != "All": q += f" AND City='{city}'"
    if rtype != "All": q += f" AND Type='{rtype}'"
    df = run_query(q)
    st.markdown(f'<div class="row-count">{len(df)} receivers found</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# MANAGE DATA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Manage Data":
    st.markdown("""<div class="page-header">
        <h1>Manage Data</h1>
        <p>Add, update, or remove food listings from the system</p>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["➕  Add Listing", "✏️  Update Listing", "🗑️  Delete Listing"])

    with tab1:
        with st.form("add_food", clear_on_submit=True):
            c1,c2 = st.columns(2)
            food_name   = c1.text_input("Food Name")
            quantity    = c2.number_input("Quantity", min_value=1)
            c3,c4 = st.columns(2)
            expiry      = c3.date_input("Expiry Date")
            provider_id = c4.number_input("Provider ID", min_value=1)
            c5,c6 = st.columns(2)
            food_type   = c5.selectbox("Food Type", ["Vegetarian","Non-Vegetarian","Vegan"])
            meal_type   = c6.selectbox("Meal Type", ["Breakfast","Lunch","Dinner","Snacks"])
            location    = st.text_input("Location")
            if st.form_submit_button("Add Food Listing", use_container_width=True):
                if food_name and location:
                    conn = get_connection(); cur = conn.cursor()
                    cur.execute("INSERT INTO food_listings (Food_Name,Quantity,Expiry_Date,Provider_ID,Location,Food_Type,Meal_Type) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                                (food_name,quantity,expiry,provider_id,location,food_type,meal_type))
                    conn.commit(); conn.close()
                    st.success(f"✅ '{food_name}' added successfully!")
                else:
                    st.error("Food Name and Location are required.")

    with tab2:
        food_id = st.number_input("Food ID to update", min_value=1, key="uid")
        with st.form("update_food"):
            c1,c2 = st.columns(2)
            new_qty    = c1.number_input("New Quantity", min_value=1)
            new_expiry = c2.date_input("New Expiry Date")
            new_ftype  = st.selectbox("Food Type", ["Vegetarian","Non-Vegetarian","Vegan"])
            if st.form_submit_button("Update Listing", use_container_width=True):
                conn = get_connection(); cur = conn.cursor()
                cur.execute("UPDATE food_listings SET Quantity=%s,Expiry_Date=%s,Food_Type=%s WHERE Food_ID=%s",
                            (new_qty,new_expiry,new_ftype,food_id))
                conn.commit(); rows=cur.rowcount; conn.close()
                st.error(f"Food ID {food_id} not found.") if rows==0 else st.success(f"✅ Food ID {food_id} updated!")

    with tab3:
        st.warning("⚠️ This action is permanent and cannot be undone.")
        food_id = st.number_input("Food ID to delete", min_value=1, key="did")
        if st.button("Delete Listing", type="primary", use_container_width=True):
            conn = get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM food_listings WHERE Food_ID=%s", (food_id,))
            conn.commit(); rows=cur.rowcount; conn.close()
            st.error(f"Food ID {food_id} not found.") if rows==0 else st.success(f"✅ Food ID {food_id} deleted!")
