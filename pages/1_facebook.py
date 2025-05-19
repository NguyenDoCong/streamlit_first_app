import streamlit as st
from database_utils import get_distinct_user_ids_from_db

def display_facebook_users():
    st.title('Danh sách người dùng Facebook')
    