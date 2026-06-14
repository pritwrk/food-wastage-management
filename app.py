import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="7836",
        database="food_wastage_db"
    )

def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="Food Wastage Management", layout="wide")
st.title("🍱 Local Food Wastage Management System")

menu = st.sidebar.selectbox("Menu", [
    "Dashboard",
    "SQL Queries",
    "Food Listings",
    "Providers",
    "Receivers",
    "CRUD Operations"
])

if menu == "Dashboard":
    st.subheader("Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Providers", run_query("SELECT COUNT(*) as c FROM providers")["c"][0])
    col2.metric("Total Receivers", run_query("SELECT COUNT(*) as c FROM receivers")["c"][0])
    col3.metric("Food Listings", run_query("SELECT COUNT(*) as c FROM food_listings")["c"][0])
    col4.metric("Total Claims", run_query("SELECT COUNT(*) as c FROM claims")["c"][0])

    st.divider()

    # Chart 1 - Claims Status Pie Chart
    col_a, col_b = st.columns(2)
    with col_a:
        df_status = run_query("SELECT Status, COUNT(*) as count FROM claims GROUP BY Status")
        fig1 = px.pie(df_status, names="Status", values="count",
                      title="Claims Status Distribution",
                      color_discrete_map={"Completed": "#2ecc71", "Pending": "#f39c12", "Cancelled": "#e74c3c"})
        fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig1, use_container_width=True)

    # Chart 2 - Meal Type Bar Chart
    with col_b:
        df_ftype = run_query("SELECT Food_Type, COUNT(*) as count FROM food_listings GROUP BY Food_Type ORDER BY count DESC")
        fig2 = px.bar(df_ftype, x="Food_Type", y="count",
                      title="Food Type Distribution",
                      color="Food_Type",
                      color_discrete_map={"Vegetarian": "#2ecc71", "Non-Vegetarian": "#e74c3c", "Vegan": "#3498db"})
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    st.divider()

    # Chart 3 - Top 10 Cities Bar Chart
   # Chart 3 - Provider Type by Total Quantity
    df_ptype = run_query("SELECT p.Type, SUM(fl.Quantity) as total_quantity FROM providers p JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID GROUP BY p.Type ORDER BY total_quantity DESC")
    fig3 = px.bar(df_ptype, x="Type", y="total_quantity",
                  title="Total Food Quantity by Provider Type",
                  color="Type",
                  color_discrete_sequence=["#2ecc71", "#3498db", "#e74c3c", "#f39c12"])
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
elif menu == "SQL Queries":
    st.subheader("SQL Query Results")
    queries = {
        "1. Providers per City": "SELECT City, COUNT(*) as total_providers FROM providers GROUP BY City ORDER BY total_providers DESC",
        "2. Provider Type Contribution": "SELECT Type, COUNT(*) as total FROM providers GROUP BY Type ORDER BY total DESC",
        "3. Top 10 Receivers by Claims": "SELECT r.Name, r.Type, COUNT(c.Claim_ID) as total_claims FROM receivers r JOIN claims c ON r.Receiver_ID = c.Receiver_ID GROUP BY r.Receiver_ID, r.Name, r.Type ORDER BY total_claims DESC LIMIT 10",
        "4. Total Food Quantity": "SELECT SUM(Quantity) as total_quantity FROM food_listings",
        "5. City with Most Listings": "SELECT Location, COUNT(*) as total_listings FROM food_listings GROUP BY Location ORDER BY total_listings DESC",
        "6. Common Food Types": "SELECT Food_Type, COUNT(*) as count FROM food_listings GROUP BY Food_Type ORDER BY count DESC",
        "7. Claims per Food Item": "SELECT fl.Food_Name, COUNT(c.Claim_ID) as total_claims FROM food_listings fl JOIN claims c ON fl.Food_ID = c.Food_ID GROUP BY fl.Food_ID, fl.Food_Name ORDER BY total_claims DESC LIMIT 10",
        "8. Top Providers by Successful Claims": "SELECT p.Name, p.Type, COUNT(c.Claim_ID) as successful_claims FROM providers p JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID JOIN claims c ON fl.Food_ID = c.Food_ID WHERE c.Status = 'Completed' GROUP BY p.Provider_ID, p.Name, p.Type ORDER BY successful_claims DESC LIMIT 10",
        "9. Claims Status %": "SELECT Status, COUNT(*) as count, ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) as percentage FROM claims GROUP BY Status",
        "10. Avg Quantity per Claim": "SELECT ROUND(AVG(fl.Quantity), 2) as avg_quantity FROM claims c JOIN food_listings fl ON c.Food_ID = fl.Food_ID WHERE c.Status = 'Completed'",
        "11. Most Claimed Meal Type": "SELECT fl.Meal_Type, COUNT(c.Claim_ID) as total_claims FROM food_listings fl JOIN claims c ON fl.Food_ID = c.Food_ID GROUP BY fl.Meal_Type ORDER BY total_claims DESC",
        "12. Total Donated per Provider": "SELECT p.Name, SUM(fl.Quantity) as total_donated FROM providers p JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID GROUP BY p.Provider_ID, p.Name ORDER BY total_donated DESC LIMIT 10",
        "13. City-wise Claim Success Rate": "SELECT fl.Location, COUNT(c.Claim_ID) as total_claims, ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate FROM food_listings fl JOIN claims c ON fl.Food_ID = c.Food_ID GROUP BY fl.Location ORDER BY success_rate DESC",
        "14. Receivers per City": "SELECT City, COUNT(*) as total_receivers FROM receivers GROUP BY City ORDER BY total_receivers DESC",
        "15. Claims by Provider Type": "SELECT p.Type, COUNT(c.Claim_ID) as total_claims FROM providers p JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID JOIN claims c ON fl.Food_ID = c.Food_ID GROUP BY p.Type ORDER BY total_claims DESC",
    }
    selected = st.selectbox("Query select karo", list(queries.keys()))
    df = run_query(queries[selected])
    st.dataframe(df, use_container_width=True)

elif menu == "Food Listings":
    st.subheader("Food Listings with Filters")
    col1, col2, col3 = st.columns(3)
    cities = ["All"] + list(run_query("SELECT DISTINCT Location FROM food_listings ORDER BY Location")["Location"])
    food_types = ["All"] + list(run_query("SELECT DISTINCT Food_Type FROM food_listings")["Food_Type"])
    meal_types = ["All"] + list(run_query("SELECT DISTINCT Meal_Type FROM food_listings")["Meal_Type"])
    city = col1.selectbox("City", cities)
    food_type = col2.selectbox("Food Type", food_types)
    meal_type = col3.selectbox("Meal Type", meal_types)

    query = "SELECT fl.*, p.Name as Provider_Name, p.Contact FROM food_listings fl JOIN providers p ON fl.Provider_ID = p.Provider_ID WHERE 1=1"
    if city != "All": query += f" AND fl.Location = '{city}'"
    if food_type != "All": query += f" AND fl.Food_Type = '{food_type}'"
    if meal_type != "All": query += f" AND fl.Meal_Type = '{meal_type}'"

    st.dataframe(run_query(query), use_container_width=True)

elif menu == "Providers":
    st.subheader("Providers Contact Details")
    col1, col2 = st.columns(2)
    cities = ["All"] + list(run_query("SELECT DISTINCT City FROM providers ORDER BY City")["City"])
    types = ["All"] + list(run_query("SELECT DISTINCT Type FROM providers ORDER BY Type")["Type"])
    city = col1.selectbox("City", cities)
    ptype = col2.selectbox("Type", types)
    
    query = "SELECT Name, Type, City, Contact FROM providers WHERE 1=1"
    if city != "All": query += f" AND City = '{city}'"
    if ptype != "All": query += f" AND Type = '{ptype}'"
    
    st.dataframe(run_query(query), use_container_width=True)    

elif menu == "Receivers":
    st.subheader("Receivers Contact Details")
    col1, col2 = st.columns(2)
    cities = ["All"] + list(run_query("SELECT DISTINCT City FROM receivers ORDER BY City")["City"])
    types = ["All"] + list(run_query("SELECT DISTINCT Type FROM receivers ORDER BY Type")["Type"])
    city = col1.selectbox("City", cities)
    rtype = col2.selectbox("Type", types)
    
    query = "SELECT * FROM receivers WHERE 1=1"
    if city != "All": query += f" AND City = '{city}'"
    if rtype != "All": query += f" AND Type = '{rtype}'"
    
    st.dataframe(run_query(query), use_container_width=True)

elif menu == "CRUD Operations":
    st.subheader("CRUD Operations")
    
    operation = st.radio("Operation", ["Add", "Update", "Delete"], horizontal=True)
    
    if operation == "Add":
        st.subheader("Add New Food Listing")
        with st.form("add_food"):
            food_name = st.text_input("Food Name")
            quantity = st.number_input("Quantity", min_value=1)
            expiry = st.date_input("Expiry Date")
            provider_id = st.number_input("Provider ID", min_value=1)
            location = st.text_input("Location")
            food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
            submitted = st.form_submit_button("Add Food")
            if submitted:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO food_listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type) VALUES (%s,%s,%s,%s,(SELECT Type FROM providers WHERE Provider_ID=%s),%s,%s,%s)",
                    (food_name, quantity, expiry, provider_id, provider_id, location, food_type, meal_type)
                )
                conn.commit()
                conn.close()
                st.success("Food listing added!")

    elif operation == "Update":
        st.subheader("Update Food Listing")
        food_id = st.number_input("Food ID to update", min_value=1)
        with st.form("update_food"):
            new_quantity = st.number_input("New Quantity", min_value=1)
            new_expiry = st.date_input("New Expiry Date")
            new_status = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            submitted = st.form_submit_button("Update")
            if submitted:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE food_listings SET Quantity=%s, Expiry_Date=%s, Food_Type=%s WHERE Food_ID=%s",
                    (new_quantity, new_expiry, new_status, food_id)
                )
                conn.commit()
                if cursor.rowcount == 0:
                    st.error("Food ID nahi mila!")
                else:
                    st.success(f"Food ID {food_id} updated!")
                conn.close()

    elif operation == "Delete":
        st.subheader("Delete Food Listing")
        st.warning("Ye action permanent hai!")
        food_id = st.number_input("Food ID to delete", min_value=1)
        if st.button("Delete"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM food_listings WHERE Food_ID=%s", (food_id,))
            conn.commit()
            conn.close()
            if cursor.rowcount == 0:
                st.error("Food ID nahi mila!")
            else:
                st.success(f"Food ID {food_id} deleted!")