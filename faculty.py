
import re
import streamlit as st
from database import create_usertable, add_userdata, login_user, add_component_request, add_reimbursement_request, get_user_component_requests, get_user_reimbursement_requests

# Function to apply styling to request status
def get_status_style(status):
    if status == "Approved":
        return "color: green;"
    elif status == "Denied":
        return "color: red;"
    else:
        return ""

def is_valid_email(email):
    return re.match(r"[^@]+@pesu\.pes\.edu$", email)

def is_valid_phone(phone):
    return re.match(r"^[6-9]\d{9}$", phone)

def main():
    st.title("Component Purchase and Reimbursement App")

    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")

    elif choice == "Login":
        st.subheader("Login Section")

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login"):
            create_usertable()
            result = login_user(username, password)
            if result:
                st.success("Logged In as {}".format(username))

                task = st.selectbox("Task", ["Add Component Request", "Add Reimbursement Request", "View Component Requests", "View Reimbursement Requests"])
                if task == "Add Component Request":
                    st.subheader("Add Component Request")
                    component_name = st.text_input("Component Name")
                    price = st.number_input("Price", min_value=0.0)
                    retailer_name = st.text_input("Retailer Name")
                    project_name = st.text_input("Project Name")
                    if st.button("Submit Request"):
                        add_component_request(username, component_name, price, retailer_name, "", project_name)


                elif task == "Add Reimbursement Request":
                    st.subheader("Add Reimbursement Request")
                    component_name = st.text_input("Component Name")
                    price = st.number_input("Price", min_value=0.0)
                    retailer_name = st.text_input("Retailer Name")
                    project_name = st.text_input("Project Name")
                    if st.button("Submit Request"):
                        add_reimbursement_request(username, component_name, price, retailer_name, "", project_name)


                elif task == "View Component Requests":
                    st.subheader("Your Component Requests")
                    user_requests = get_user_component_requests(username)

                    for request in user_requests:
                        st.markdown('---')
                        st.markdown(f'Request ID: {request[0]}', unsafe_allow_html=True)
                        st.markdown(f'Component Name: {request[2]}', unsafe_allow_html=True)
                        st.markdown(f'Price: {request[3]}', unsafe_allow_html=True)
                        st.markdown(f'Retailer Name: {request[4]}', unsafe_allow_html=True)
                        st.markdown(f'Project Name: {request[6]}', unsafe_allow_html=True)
                        description = st.text(request[-2])
                        st.markdown(f'Status: {request[-1]}', unsafe_allow_html=True)

                elif task == "View Reimbursement Requests":
                    st.subheader("Your Reimbursement Requests")
                    user_reimbursements = get_user_reimbursement_requests(username)

                    for request in user_reimbursements:
                        st.markdown('---')
                        st.markdown(f'Request ID: {request[0]}', unsafe_allow_html=True)
                        st.markdown(f'Component Name: {request[2]}', unsafe_allow_html=True)
                        st.markdown(f'Price: {request[3]}', unsafe_allow_html=True)
                        st.markdown(f'Retailer Name: {request[4]}', unsafe_allow_html=True)
                        st.markdown(f'Project Name: {request[6]}', unsafe_allow_html=True)
                        description = st.text(request[-2])
                        st.markdown(f'Status: {request[-1]}', unsafe_allow_html=True)

            else:
                st.warning("Incorrect Username/Password")

    elif choice == "SignUp":
        st.subheader("Create a New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        new_email = st.text_input("Email")

        # Dialog box for valid email format
        if not is_valid_email(new_email) and new_email != "":
            st.warning("Invalid email format. Please use a valid email id: @pesu.pes.edu")

        new_phone = st.text_input("Phone Number")

        # Dialog box for valid phone number format
        if not is_valid_phone(new_phone) and new_phone != "":
            st.warning("Invalid phone number format. Please use a valid 10-digit phone number starting with 6-9.")

        if st.button("Signup") and is_valid_email(new_email) and is_valid_phone(new_phone):
            create_usertable()
            add_userdata(new_user, new_password, new_email, new_phone)
            st.success("You have successfully created an account")
            st.info("Go to the Login Menu to log in")


if __name__ == '__main__':
    main()
