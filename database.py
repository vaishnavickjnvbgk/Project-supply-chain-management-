import sqlite3
from datetime import datetime
import streamlit as st
def create_usertable():
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT, email TEXT, phone TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS componentstable(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, component_name TEXT, price REAL, retailer_name TEXT, component_description TEXT, project_name TEXT, status TEXT, description TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS reimbursementstable(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, component_name TEXT, price REAL, retailer_name TEXT, image TEXT, project_name TEXT, status TEXT, description TEXT)')

    # Use a try-except block to catch and ignore the error if the column already exists
    try:
        c.execute("ALTER TABLE reimbursementstable ADD COLUMN description TEXT")
    except sqlite3.OperationalError:
        pass

    # Add trigger to automatically deny requests with insufficient details for component requests
    c.execute('''CREATE TRIGGER IF NOT EXISTS component_trigger
                BEFORE INSERT ON componentstable
                WHEN NEW.component_name = '' OR NEW.price = 0.0 OR NEW.retailer_name = '' OR NEW.project_name = '' OR NEW.component_description = ''
                BEGIN
                    SELECT RAISE(ABORT, 'Insufficient details for component request');
                END''')

    # Add trigger to automatically deny requests with insufficient details for reimbursement requests
    c.execute('''CREATE TRIGGER IF NOT EXISTS reimbursement_trigger
                BEFORE INSERT ON reimbursementstable
                WHEN NEW.component_name = '' OR NEW.price = 0.0 OR NEW.retailer_name = '' OR NEW.project_name = ''
                BEGIN
                    UPDATE reimbursementstable SET status = 'Denied' WHERE id = NEW.id;
                END''')
    conn.commit()
    conn.close()


    c.execute('''CREATE FUNCTION is_valid_email(email TEXT) RETURNS INTEGER
                BEGIN
                    RETURN CASE
                        WHEN email LIKE '%@pesu.pes.edu' THEN 1
                        ELSE 0
                    END;
                END;''')

    conn.commit()
    conn.close()


    c.execute('''CREATE PROCEDURE is_valid_phone_proc(phone TEXT)
                BEGIN
                    SELECT CASE
                        WHEN LENGTH(phone) = 10 AND SUBSTR(phone, 1, 1) IN ('6', '7', '8', '9') AND SUBSTR(phone, 2) GLOB '[0-9]' THEN 1
                        ELSE 0
                    END;
                END;''')

    conn.commit()
    conn.close()
        

def join_requests():
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    join_query = '''
        SELECT reimbursementstable.id, reimbursementstable.username, reimbursementstable.component_name,
               reimbursementstable.price, reimbursementstable.retailer_name, reimbursementstable.image,
               reimbursementstable.project_name, reimbursementstable.status, reimbursementstable.description,
               userstable.email, userstable.phone
        FROM reimbursementstable
        INNER JOIN userstable ON reimbursementstable.username = userstable.username
        WHERE reimbursementstable.status != "Deleted"
    '''
    data = c.execute(join_query).fetchall()
    conn.close()
    return data


def is_valid_email(email):
    return email.endswith("@pesu.pes.edu")

def is_valid_phone(phone):
    return len(phone) == 10 and phone[0] in ['6', '7', '8', '9'] and phone[1:].isdigit()


def call_is_valid_phone_proc(phone):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()

    # Call the is_valid_phone_proc procedure and fetch the result
    result = c.execute('CALL is_valid_phone_proc(?)', (phone,)).fetchone()[0]

    conn.close()

    return result

def add_userdata(username, password, email, phone):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()

    if not is_valid_email(email):
        print("Incorrect email format. Please use an email ending with @pesu.pes.edu")
        conn.close()
        return

    if not is_valid_phone(phone):
        print("Incorrect phone number format. Please use a 10-digit number starting with 6, 7, 8, or 9.")
        conn.close()
        return

    if not email.endswith("@pesu.pes.edu"):
        print("Incorrect email format. Please use an email ending with @pesu.pes.edu")
        conn.close()
        return

    c.execute('INSERT INTO userstable(username, password, email, phone) VALUES (?, ?, ?, ?)', (username, password, email, phone))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    data = c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()
    return data

def add_component_request(username, component_name, price, retailer_name, component_description, project_name):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()

    # Check if all required fields are provided
    if not all([component_name, price, retailer_name, project_name]):
        st.warning("Please provide sufficient details for the component request.")
        conn.close()
        return

    # Generate a unique request ID based on the current timestamp
    request_id = int(datetime.timestamp(datetime.now()))

    c.execute('INSERT INTO componentstable(id, username, component_name, price, retailer_name, project_name, status, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
              (request_id, username, component_name, price, retailer_name, project_name, 'Pending', ''))
    conn.commit()
    conn.close()

    # Display success message
    st.success("Request submitted successfully.")

def add_reimbursement_request(username, component_name, price, retailer_name, image, project_name):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()

    # Check if all required fields are provided
    if not all([component_name, price, retailer_name, project_name]):
        st.warning("Please provide sufficient details for the reimbursement request.")
        conn.close()
        return

    # Generate a unique request ID based on the current timestamp
    request_id = int(datetime.timestamp(datetime.now()))

    c.execute('INSERT INTO reimbursementstable(id, username, component_name, price, retailer_name, image, project_name, status, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (request_id, username, component_name, price, retailer_name, image, project_name, 'Pending', ''))
    conn.commit()
    conn.close()

    # Display success message
    st.success("Reimbursement request submitted successfully.")


def update_description(table, id, description):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    c.execute(f'UPDATE {table} SET description = ? WHERE id = ?', (description, id))
    conn.commit()
    conn.close()

def get_description(table, id):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    description = c.execute(f'SELECT description FROM {table} WHERE id = ?', (id,)).fetchone()
    conn.close()
    return description

def login_user(username, password):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    data = c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username, password)).fetchall()
    conn.close()
    return data

def get_user_component_requests(username):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    data = c.execute('SELECT * FROM componentstable WHERE username = ?', (username,)).fetchall()
    conn.close()
    return data

def get_user_reimbursement_requests(username):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    data = c.execute('SELECT * FROM reimbursementstable WHERE username = ?', (username,)).fetchall()
    conn.close()
    return data

def get_user_requests(username):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    component_requests = c.execute('SELECT * FROM componentstable WHERE username = ?', (username,)).fetchall()
    reimbursement_requests = c.execute('SELECT * FROM reimbursementstable WHERE username = ?', (username,)).fetchall()
    conn.close()
    return component_requests + reimbursement_requests

def get_user_reimbursements(username):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    data = c.execute('SELECT * FROM reimbursementstable WHERE username = ?', (username,)).fetchall()
    conn.close()
    return data

def approve_request(table, id):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    c.execute(f'UPDATE {table} SET status = "Approved" WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def deny_request(table, id):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    c.execute(f'UPDATE {table} SET status = "Denied" WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def delete_request(table, id):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    c.execute(f'DELETE FROM {table} WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def get_all_requests():
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    data = c.execute('SELECT * FROM componentstable WHERE status != "Deleted" UNION ALL SELECT * FROM reimbursementstable WHERE status != "Deleted"').fetchall()
    conn.close()
    return data


def get_pending_requests_all():
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    data = c.execute('SELECT * FROM componentstable WHERE status = "Pending" UNION ALL SELECT * FROM reimbursementstable WHERE status = "Pending"').fetchall()
    conn.close()
    return data

def get_component_requests():
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    data = c.execute('SELECT * FROM componentstable WHERE status != "Deleted"').fetchall()
    conn.close()
    return data

def count_total_requests_all(username):
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    total_requests = c.execute('SELECT COUNT() FROM componentstable WHERE username = ? UNION ALL SELECT COUNT() FROM reimbursementstable WHERE username = ?', (username, username)).fetchall()
    total = sum(total_requests[0] + total_requests[1])
    conn.close()
    return total

def get_reimbursement_requests():
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    data = c.execute('SELECT * FROM reimbursementstable WHERE status != "Deleted"').fetchall()
    conn.close()
    return data

def get_pending_component_requests():
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    data = c.execute('SELECT * FROM componentstable WHERE status = "Pending"').fetchall()
    conn.close()
    return data

def get_pending_reimbursement_requests():
    conn = sqlite3.connect('dbmsProj.db')
    c = conn.cursor()
    data = c.execute('SELECT * FROM reimbursementstable WHERE status = "Pending"').fetchall()
    conn.close()
    return data


if __name__ == '__main__':
    create_usertable()
