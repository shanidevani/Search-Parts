import streamlit as st
import pandas as pd
import numpy as np
import io

# Sets the app to use a wide layout for a more spacious feel.
st.set_page_config(layout="wide")

# --- Login Credentials ---
LOGIN_CREDENTIALS = {
    "ARMMACHAWASASADMIN": "Smart@123456",
    "MATOLASASADMIN": "Smart@123456",
    "MATOLARIOSASADMIN": "Smart@123456",
    "MAPUTOSASADMIN": "Smart@123456",
    "CHOUPALSASADMIN": "Smart@123456",
    "MACHAWASASADMIN": "Smart@123456",
    "ARMBEIRASASADMIN": "Smart@123456",
    "BEIRASASADMIN": "Smart@123456",
    "NAMPULASASADMIN": "Smart@123456",
    "CHEMOIOSASADMIN": "Smart@123456",
}

# --- Login Page Logic ---
def login_page():
    """Displays the login form and handles authentication."""
    st.title("Login to Search Parts")
    st.markdown("---")
    
    with st.form("login_form"):
        st.subheader("Please log in to continue")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Log In")

        if login_button:
            if username in LOGIN_CREDENTIALS and LOGIN_CREDENTIALS[username] == password:
                st.session_state["authenticated"] = True
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

# Check if user is authenticated
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- Main Application Logic ---
if st.session_state["authenticated"]:
    # --- Logout Button ---
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()
        
    # --- Main Application Layout ---
    st.title("Search Parts")
    st.markdown("---")
    
    # --- Data Loading ---
    try:
        # Use the raw GitHub URL for the CSV file.
        file_path = "https://raw.githubusercontent.com/shanidevani/Search-Parts/main/M%20APPLICATIONS(FRAM%20ENG).csv"
        
        # Read the CSV file with 'latin-1' encoding and skip bad lines.
        df = pd.read_csv(file_path, encoding='latin-1', on_bad_lines='skip')

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.stop()

    # --- Initialize filtered DataFrame ---
    filtered_df = df.copy()

    # Filter Group 1: Category & Position
    # with st.expander("Category and Position"):
    tab5, tab1, tab2, tab3, tab4 = st.columns(5)
    category = tab5.selectbox("Select Category (CAT)", ['All'] + sorted(df['CAT'].dropna().unique()))
    front_rear = tab1.checkbox("F/R (Front/Rear)")
    left_right = tab2.checkbox("L/R (Left/Right)")
    upper_lower = tab3.checkbox("U/L (Upper/Lower)")
    in_out = tab4.checkbox("I/O (In/Out)")

    if category != 'All':
        filtered_df = filtered_df[filtered_df['CAT'] == category]

    # Apply the F/R, L/R, U/L, I/O filter
    if front_rear or left_right or upper_lower or in_out:
        position_mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
        
        if front_rear:
            position_mask |= filtered_df['F/R'].notna()
        if left_right:
            position_mask |= filtered_df['L/R'].notna()
        if upper_lower:
            position_mask |= filtered_df['U/L'].notna()
        if in_out:
            position_mask |= filtered_df['I/O'].notna()
            
        filtered_df = filtered_df[position_mask]

    # Filter Group 2: Car, Model, and Year
    # with st.expander("Car and Model"):
    col1, col2, col3, col4, col5 = st.columns(5)
    car_list = ['All'] + sorted(df['CAR'].dropna().unique())
    selected_car = col1.selectbox("Select Car (CAR)", car_list)


    if selected_car != 'All':
        model_list = ['All'] + sorted(df[df['CAR'] == selected_car]['MODEL.1'].dropna().unique())
    else:
        model_list = ['All'] + sorted(df['MODEL.1'].dropna().unique())

    selected_model = col2.selectbox("Select Model (MODEL)", model_list)

    all_years = sorted([int(y) for y in set(df['ANO DE I.'].dropna().unique()) | set(df['ANO FI.'].dropna().unique())])
    selected_year = col3.selectbox("Select Year", ['All'] + all_years)

    if selected_car != 'All':
        filtered_df = filtered_df[filtered_df['CAR'] == selected_car]
    if selected_model != 'All':
        filtered_df = filtered_df[filtered_df['MODEL.1'] == selected_model]
    if selected_year != 'All':
        filtered_df = filtered_df[
            (filtered_df['ANO DE I.'] <= selected_year) & 
            (filtered_df['ANO FI.'] >= selected_year)
        ]

    # Filter Group 3: Frame or Engine No.
    # with st.expander("Frame/Engine Search"):
    frame_engine_search = col4.text_input("Enter Frame No. or Engine No.")
    if frame_engine_search:
        search_text = frame_engine_search.lower().strip()
        filtered_df = filtered_df[
            (filtered_df['FRAME'].astype(str).str.lower().str.contains(search_text, na=False)) |
            (filtered_df['ENGINE'].astype(str).str.lower().str.contains(search_text, na=False))
        ]

    # Filter Group 4: Part No.
    # with st.expander("Part No. Search"):
    part_no_search = col5.text_input("Search Part No.")
    if part_no_search:
        search_text = part_no_search.lower().strip()
        filtered_df = filtered_df[
            filtered_df['PART NO.'].astype(str).str.lower().str.contains(search_text, na=False)
        ]

    # --- Display Results ---
    if not filtered_df.empty:
        st.subheader("Filtered Part Numbers:")
        st.dataframe(filtered_df[['PART NO.']].reset_index(drop=True), hide_index=True)
    else:
        st.warning("No part numbers found with the selected filters.")
else:
    login_page()
