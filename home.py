
import streamlit as st
from faculty import main as faculty_page
from university import university_page

def home_page():
    st.title("Component Purchase and Reimbursement Request")
    st.write("Welcome to the Home Page")

    page = st.selectbox("Select a Page", ["Home", "Faculty", "University"])

    if page == "Home":
        st.subheader("Home Page")
        st.write("This is the home page. Choose a page from the sidebar.")

    elif page == "Faculty":
        faculty_page()

    elif page == "University":
        university_page()

if __name__ == '__main__':
    home_page()
