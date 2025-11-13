import streamlit as st
import pandas as pd
import mysql.connector as sql
import hashlib
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn.objects as so
from datetime import datetime

# ---- DB Connection ----
def dbconnect():
    return sql.connect(
        host='localhost',
        user='root',
        password='welcome1',
        database='cqms'
    )
st.set_page_config(page_title="Client Query Management System",
layout="wide")

# ---- Password Hashing ----
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------ Time for auto refresh -----

# ---- Login Function ----
def login(username, password, role):
    hashed_password = hash_password(password)
    conn = dbconnect()
    cursor = conn.cursor()

    query = """
        SELECT user_id, user_name, user_mobile, user_role
        FROM user_detail
        WHERE user_name = %s AND user_password = %s AND user_role = %s
    """
    cursor.execute(query, (username, hashed_password, role))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result

# ---- Get Email ----
def get_user_email(username):
    conn = dbconnect()
    cursor = conn.cursor()

    query = "SELECT user_email FROM user_detail WHERE user_name = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result[0] if result else None

# ---- Page Navigation ----
def go_to_login():
    st.session_state.page = "login"

def go_to_dashboard():
    st.session_state.page = "dashboard"

def go_to_query():
    st.session_state.page = "Query"

def go_to_admin():
    st.session_state.page = "Admin"

def fetch_by_status(status):
    conn = dbconnect()
    cursor = conn.cursor()
    Status_Query = """
        SELECT query_id, client_email, client_mobile, query_heading, 
               query_description, status, date_raised, date_closed, user_id 
        FROM query_detail WHERE status=%s
    """
    cursor.execute(Status_Query, (status,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def highlight_above_22(val):
    if val > avg_resolve_days:
        color = '#FFC107' 
    elif val <= avg_resolve_days:
        color = 'lightgreen' 
    return f'background-color: {color}'
    
# ---- Style ----

page_style = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #f0f8ff;
}
</style>
"""
st.markdown("""
<style>
div[data-testid="stselectbox"] select {
    background-color: #FFF8DC !important;
    color: #000 !important;
    border: 1px solid #888 !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)



# ---- Initialize Session State ----
for key in ["page", "username", "user_id", "user_mobile"]:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.page is None:
    st.session_state.page = "login"

# ---- UI ----
st.title("Client Query Management System")

# ------------------ LOGIN PAGE ------------------
if st.session_state.page == "login":
    #col1, col2, col3 = st.columns([1,2,1])
    #with col2:
    #   st.image("Logo.png", width=200)
    
    #st.header("Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Client","Support","Admin"])
    st.write("Selected: ", role)

    if st.button("Login"):
        user = login(username, password, role)
        if user:
            st.session_state.username = user[1]
            st.session_state.user_mobile = user[2]
            st.session_state.user_id = user[0]

            st.success(f"Login Successful! Welcome {user[1]}")

            if role == "Client":
                go_to_query()
            elif role == "Support":
                go_to_dashboard()
            else:
                go_to_admin()

            st.rerun()
        else:
            st.error("Invalid Username/Password/Role")

# ------------------ QUERY PAGE (Client) ------------------
elif st.session_state.page == "Query":

    
    st.write(f"Welcome *{st.session_state.username}*")

    page = st.sidebar.radio("Go to", ["Home", "Submit Query", "Track Query", "Logout"])

    if page == "Home":
        st.title("🏠 Home Page")
        
    elif page == "Submit Query":
        st.header("Submit Query")

    # Fetch Query Heading from DB
        conn = dbconnect()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT query_heading FROM query_detail")
        headings = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        selected_heading = st.selectbox("Select Query Heading", headings)
        query_description = st.text_area("Enter Query Description")

        if st.button("Submit Query"):
            if not (selected_heading and query_description):
                st.warning("Please fill required fields!")
            else:
                user_email = get_user_email(st.session_state.username)
                conn = dbconnect()
                cursor = conn.cursor()

                insert_query = """
                INSERT INTO query_detail 
                (query_heading, query_description, status, date_raised, client_email, client_mobile, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

                cursor.execute(insert_query, (
                selected_heading,
                query_description,
                "Open",
                datetime.now(),
                user_email,
                st.session_state.user_mobile,
                st.session_state.user_id
            ))

                conn.commit()
                cursor.close()
                conn.close()

                st.success("✅ Query Submitted Successfully!")
    
    elif page == ("Track Query"):
        user_id = st.session_state.user_id


        if st.button("Track Query"):
            conn = dbconnect()
            cursor = conn.cursor()

            Track_Query = """
            SELECT query_id, client_email, client_mobile, query_heading, 
            query_description, status, date_raised  
            FROM query_detail where user_id=%s
            """
            cursor.execute(Track_Query, (user_id,))
            result = cursor.fetchall()

            
            if result:
                df = pd.DataFrame(result, columns=["query_id", "client_email", "client_mobile", "query_heading", 
                "query_description", "status", "date_raised"])
                
                df = df.rename(columns =
            {"query_id": "Query ID",
            "client_email": "Email ID",
            "client_mobile": "Mobile Number",
            "query_heading": "Query Heading",
            "query_description": "Query Description",
            "status": "Status",
            "date_raised": "Date Raised"})
                st.dataframe(df, hide_index= True)

            else:
                st.warning("No data found!")

    elif page == "Logout":
        st.title("Logout")
        st.button("Logout")
        go_to_login()

# ------------------ Admin PAGE ------------------

elif st.session_state.page == "Admin":
    def user_exists(user_name, user_email):
        conn = dbconnect()
        cursor = conn.cursor()

        query = """
        SELECT user_id 
        FROM user_detail 
        WHERE user_name = %s OR user_email = %s
        """

        cursor.execute(query, (user_name, user_email))
        result = cursor.fetchone()

        conn.close()

        return result is not None

    st.header("User Management")

    st.sidebar.title("Navigation")

    page = st.sidebar.radio("Go to", ["Home", "User Management", "Logout"])

    if page == "Home":
        st.title("Home Page")
        st.write("Welcome!")
        
    elif page == "User Management":
        st.title("User Management")
        user_fullname = st.text_input("User Fullname")
        user_name = st.text_input("User Name") 
        user_mobile = st.text_input("User Mobile") 
        user_email = st.text_input("User Email") 
        user_password = st.text_input("User Password", type="password") 
        user_role = st.selectbox("User Role", ["Client", "Support", "Admin"])

        if st.button("Create User"):
            if not (user_fullname and user_name and user_email and user_password):
                st.warning("Please fill required fields!")
            if user_exists(user_name, user_email):
                st.error("Username or Email already exists!")
            else:
                conn = dbconnect()
                cursor = conn.cursor()

                User_Create = """
                Insert into user_detail 
                (user_fullname, user_name, user_mobile, user_email, user_password, user_role)
                values (%s, %s, %s, %s, SHA2(%s, 256), %s)
                """
                cursor.execute(User_Create, (
                    user_fullname,
                    user_name,
                    user_mobile,
                    user_email,
                    user_password,
                    user_role
                ))

                conn.commit()
                cursor.close()
                conn.close()

                st.success("User Created Successfully!")

                cursor.close()
                conn.close()
        
    elif page == "Logout":
        st.title("Logout")
        st.button("Logout")
        go_to_login()


# ------------------ DASHBOARD PAGE (Support) ------------------

elif st.session_state.page == "dashboard":
    st.header("Support Dashboard")

    st.sidebar.title("Navigation")

    page = st.sidebar.radio("Go to", ["Home", "View Data", "Logout"])

    if page == "Home":
        st.write("Welcome!")
        conn = dbconnect()
        cursor = conn.cursor()
        
# MySQL query to get count by status
        count_status = """
        SELECT status, COUNT(*)
        FROM query_detail
        GROUP BY status;
        """

        cursor.execute(count_status)
        rows = cursor.fetchall()

# Convert results to dict {Status: Count}
        status_counts = {row[0]: row[1] for row in rows}

        open_count = status_counts.get("Open", 0)
        closed_count = status_counts.get("Closed", 0)

        
# Average days to close

        avg_days = """
        SELECT ROUND(AVG(DATEDIFF(date_closed, date_raised)),2)
        FROM query_detail;
        """
        cursor.execute(avg_days)
        avg_resolve_days = cursor.fetchone()[0]

        # User_resolved
        user_avg = """
        select user_resolved,
        round(avg(DATEDIFF(date_closed, date_raised)),2) AS avg_days
        from cqms.query_detail where status='Closed' 
        group by user_resolved order by round(avg(DATEDIFF(date_closed, date_raised)),2) asc ;
        """
        cursor.execute(user_avg)
        user_avg_days = cursor.fetchall()

        df_user_avg = pd.DataFrame(user_avg_days, columns=["user_resolved", "avg_days"])
        df_user_avg = df_user_avg.rename(columns =
        {"user_resolved": "Support Team Members",
        "avg_days": "Number of days taken to resolve the issue"} )
        df_user_avg["Number of days taken to resolve the issue"] = df_user_avg["Number of days taken to resolve the issue"].astype(float).round(2)
        styled_df = (
                    df_user_avg.style
                    .format({"Number of days taken to resolve the issue": "{:.2f}"})
                    .applymap(highlight_above_22, subset=["Number of days taken to resolve the issue"])
                    .set_properties(**{"font-weight": "bold"})
                    .set_table_styles([
                        {
            "selector": "th",
            "props": [
                ("background-color", "#0f4c81"),
                ("color", "white"),
                ("font-weight", "bold"),
                ("font-family", "Calibri"),  # Change font here
                ("font-size", "14px")        # Optional
            ]
            }
            ])
            )
        
        ## Frequent query

        heading_query = """
        select distinct(query_heading),count(1) from cqms.query_detail group by query_heading order by count(1) desc;
        """
        cursor.execute(heading_query)
        heading_query_all = cursor.fetchall()

        df_head = pd.DataFrame(heading_query_all, columns=["distinct(query_heading)", "count(1)"])
        df_head = df_head.rename(columns =
        {"distinct(query_heading)": "Query",
        "count(1)": "Number of issue raised"} )
        df_head["Number of issue raised"] = df_head["Number of issue raised"].astype(float).round(2)
        styled1_df = (
                    df_head.style
                    .format({"Number of issue raised": "{:.2f}"})
                    .applymap(highlight_above_22, subset=["Number of issue raised"])
                    .set_properties(**{"font-weight": "bold"})
                    .set_table_styles([
                        {
            "selector": "th",
            "props": [
                ("background-color", "#0f4c81"),
                ("color", "white"),
                ("font-weight", "bold"),
                ("font-family", "Calibri"),  # Change font here
                ("font-size", "14px")        # Optional
            ]
            }
            ])
            )
        
        cursor.close()
        conn.close()

# Display metrics in UI
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
        <div style='font-size:16px; font-weight:bold;'>Open Issues</div>
        <div style='font-size:26px; color: red;'>{open_count}</div>
    """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
        <div style='font-size:16px; font-weight:bold;'>Closed Issues</div>
        <div style='font-size:26px; color: green;'>{closed_count}</div>
    """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
        <div style='font-size:16px; font-weight:bold;'>Average number of days</div>
        <div style='font-size:26px; color: green;'>{avg_resolve_days}</div>
    """, unsafe_allow_html=True)

              

        st.write("## 📈 Average Days Taken to Resolve Client Issues")
        st.dataframe(styled_df, hide_index=True)
        
        st.line_chart(df_user_avg, x="Support Team Members", y="Number of days taken to resolve the issue")

        st.write("## 📈 Number issues per query")
        st.line_chart(df_head, x="Query", y="Number of issue raised")


    # ----- View data section ----
    elif page == "View Data":

        Status = st.selectbox("Status", ["Open", "Closed"])

    # Run query only when search button pressed
        if st.button("Search Queries"):
            conn = dbconnect()
            cursor = conn.cursor()

            Status_Query = """
        SELECT query_id, client_email, client_mobile, query_heading, 
        query_description, status, date_raised, date_closed, user_id 
        FROM query_detail WHERE status=%s
        """
            cursor.execute(Status_Query, (Status,))
            result = cursor.fetchall()
            cursor.close()
            conn.close()

            st.session_state['query_result'] = result  # save result
            st.session_state['search_status'] = Status  # save status option

    # Check if we have data loaded
        if 'query_result' in st.session_state:

            Status = st.session_state['search_status']
            result = st.session_state['query_result']

            df = pd.DataFrame(result, columns=[
            "query_id", "client_email", "client_mobile", "query_heading", "query_description",
            "status", "date_raised", "date_closed", "user_id"
        ])
            df = df.rename(columns =
            {"query_id": "Query ID", 
            "client_email": "Client Mail ID",
            "client_mobile": "Mobile",
            "query_heading": "Query Heading",
            "query_description": "Query Description",
            "status": "Status",
            "date_raised": "Date Raised",
            "date_closed": "Date Closed",
            "user_id": "User ID"}
            )

            st.write("### Results:")
            st.dataframe(df, hide_index=True)

        # Only allow editing when Status = "Open"
            if Status == "Open":
                st.write("### Edit Status Below")

                with st.form("update_status_form"):
                    edited_df = st.data_editor(
                        df,
                        key="query_edit_table",
                        hide_index= True,
                        disabled=[
                        "query_id", "client_email", "client_mobile", "query_heading",
                        "query_description", "date_raised", "date_closed", "user_id"
                        ]
                    )
                    save = st.form_submit_button("Save Changes")

                if save:
                    conn = dbconnect()
                    cursor = conn.cursor()
                    updates = 0

                    for index, row in edited_df.iterrows():
                        original_status = df.loc[index, "Status"]
                        new_status = row["Status"]

                        if original_status != new_status:
                            qid = row["Query ID"]
                            user_name = st.session_state.username
                            cursor.execute("""
                            UPDATE query_detail 
                            SET status = %s, 
                            date_closed = NOW(),
                            user_resolved = %s
                            WHERE query_id = %s
                            """, (new_status, user_name, qid))
                            updates += 1

                    conn.commit()
                    cursor.close()
                    conn.close()

                    if updates > 0:
                # fetch fresh data after commit and store it so when we rerun the UI will show updated rows
                        fresh_rows = fetch_by_status(Status)
                        st.session_state['query_result'] = fresh_rows

                        st.success(f"✅ {updates} record(s) updated!")
                # rerun so the page re-builds and shows the updated session_state['query_result']
                        st.rerun()
                    else:
                        st.info("No changes detected (nothing to update).")


    elif page == "Logout":
        st.title("Logout")
        st.button("Logout")
        go_to_login()


    

    


