
import streamlit as st
from database import create_usertable, approve_request, update_description, deny_request, delete_request, get_user_component_requests, get_user_reimbursement_requests, get_pending_component_requests, get_pending_reimbursement_requests,join_requests

# Function to apply styling to request status
def get_status_style(status):
    if status == "Approved":
        return "color: green;"
    elif status == "Denied":
        return "color: red;"
    else:
        return ""

def university_page():
    st.title("University Request Handling")

    # University login
    university_username = "pes"
    university_password = "pes"

    login_username = st.text_input("University Username")
    login_password = st.text_input("Password", type="password")
    login_checkbox = st.checkbox("Login")

    if login_checkbox:
        if login_username == university_username and login_password == university_password:
            st.success("Logged in as University")

            # View Faculty Requests section
            faculty_username = st.text_input("Faculty Username")

            # Dropdown for different request types
            request_type = st.selectbox("Select Request Type", ["Pending Component Requests", "Pending Reimbursement Requests", "View Component Requests", "View Reimbursement Requests"])

            # Calling the procedure to count and display the number of requests
            count_and_display_requests(request_type, faculty_username)

            # Handle different request types
            if request_type == "Pending Component Requests":
                all_requests = get_pending_component_requests()
                handle_requests(all_requests, "componentstable")
            elif request_type == "Pending Reimbursement Requests":
                all_requests = get_pending_reimbursement_requests()
                handle_requests(all_requests, "reimbursementstable")
            elif request_type == "View Component Requests":
                faculty_requests = get_user_component_requests(faculty_username)
                handle_faculty_requests(faculty_username, faculty_requests, "Component")
            elif request_type == "View Reimbursement Requests":
                faculty_requests = get_user_reimbursement_requests(faculty_username)
                handle_faculty_requests(faculty_username, faculty_requests, "Reimbursement")

            # Button to join and display all reimbursement requests
            if st.button("Join Reimbursement Requests"):
                joined_reimbursement_requests = join_requests()
                st.subheader("All Reimbursement Requests")
                handle_requests(joined_reimbursement_requests, "reimbursementstable")


        else:
            st.error("Incorrect University Username or Password")

def count_and_display_requests(request_type, faculty_username):
    if request_type == "Pending Component Requests":
        total_requests = len(get_pending_component_requests())
    elif request_type == "Pending Reimbursement Requests":
        total_requests = len(get_pending_reimbursement_requests())
    elif request_type == "View Component Requests":
        total_requests = len(get_user_component_requests(faculty_username))
    elif request_type == "View Reimbursement Requests":
        total_requests = len(get_user_reimbursement_requests(faculty_username))

    st.subheader(f"REQUESTS: {total_requests}")

def handle_faculty_requests(faculty_username, requests, request_type):
    st.subheader(f"{request_type} Requests by {faculty_username}")

    for request in requests:
        st.markdown('---')
        st.markdown(f'Request ID: {request[0]}', unsafe_allow_html=True)
        st.markdown(f'Component Name: {request[2]}', unsafe_allow_html=True)
        st.markdown(f'Price: {request[3]}', unsafe_allow_html=True)
        st.markdown(f'Retailer Name: {request[4]}', unsafe_allow_html=True)
        st.markdown(f'Project Name: {request[6]}', unsafe_allow_html=True)
        description = st.text(request[-2])
        st.markdown(f'Status: {request[-1]}', unsafe_allow_html=True)

def handle_requests(all_requests, table):
    if not all_requests:
        st.warning("No requests found.")
    else:
        st.subheader("Requests")

        to_delete = []  # Store requests to be deleted

        for request in all_requests:
            # Draw a line before each request
            st.markdown('---')

            # Display the request as a multi-line item
            st.markdown(f'Request ID: {request[0]}', unsafe_allow_html=True)
            st.markdown(f'Username: {request[1]}', unsafe_allow_html=True)
            st.markdown(f'Component Name: {request[2]}', unsafe_allow_html=True)
            st.markdown(f'Price: {request[3]}', unsafe_allow_html=True)
            st.markdown(f'Retailer Name: {request[4]}', unsafe_allow_html=True)
            st.markdown(f'Project Name: {request[6]}', unsafe_allow_html=True)
            st.markdown(f'Status: {request[7]}', unsafe_allow_html=True)

            # Generate unique key for each text area based on request ID
            description_key = f"description_{request[0]}"

            # Use checkboxes for approve and deny, along with a text area for description
            description = st.text_area(f"Description for Request {request[0]}", key=description_key)
            approve_key = f"approve_{request[0]}"
            deny_key = f"deny_{request[0]}"

            approve = st.checkbox(f"Approve {request[0]}", key=approve_key)
            deny = st.checkbox(f"Deny {request[0]}", key=deny_key)

            # Handle approval or denial
            if approve:
                # Check if description is provided before approving
                if description:
                    approve_request(table, request[0])  # Pass the table name and request ID
                    update_description(table, request[0], description)  # Pass the table name, request ID, and description
                    st.success(f"Request {request[0]} Approved")
                    to_delete.append(request[0])  # Mark for deletion
                else:
                    st.warning("Please provide a description before approving or denying the request.")
            elif deny:
                deny_request(table, request[0])  # Pass the table name and request ID
                update_description(table, request[0], description)  # Pass the table name, request ID,
                st.success(f"Request {request[0]} Denied")
                to_delete.append(request[0])  # Mark for deletion

        # Remove the marked requests from the all_requests
        all_requests = [request for request in all_requests if request[0] not in to_delete]


if __name__ == '__main__':
    create_usertable()
    university_page()
