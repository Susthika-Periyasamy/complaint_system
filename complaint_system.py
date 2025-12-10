"""
E-Complaint Justice Tracking System - Streamlit Application

SETUP INSTRUCTIONS:
1. Install dependencies:
   pip install streamlit pandas pillow

2. Save this file as: complaint_system.py

3. Run the application:
   streamlit run complaint_system.py

4. Access at: http://localhost:8501

DEFAULT LOGIN:
Admin - Email: admin@justice.gov, Password: admin123
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import hashlib
import json
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="E-Complaint Justice System",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .complaint-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background: white;
    }
    .status-badge {
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.2rem;
    }
    .status-filed { background: #ffc107; color: #000; }
    .status-review { background: #17a2b8; color: white; }
    .status-progress { background: #007bff; color: white; }
    .status-resolved { background: #28a745; color: white; }
    .status-rejected { background: #dc3545; color: white; }
</style>
""", unsafe_allow_html=True)

# Initialize data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"
COMPLAINTS_FILE = DATA_DIR / "complaints.json"
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.current_user = None
    st.session_state.page = 'login'

# Helper Functions
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_complaints():
    """Load complaints from JSON file"""
    if COMPLAINTS_FILE.exists():
        with open(COMPLAINTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_complaints(complaints):
    """Save complaints to JSON file"""
    with open(COMPLAINTS_FILE, 'w') as f:
        json.dump(complaints, f, indent=2)

def init_system():
    """Initialize system with default admin"""
    users = load_users()
    if 'admin@justice.gov' not in users:
        users['admin@justice.gov'] = {
            'name': 'Admin',
            'email': 'admin@justice.gov',
            'phone': '0000000000',
            'password': hash_password('admin123'),
            'is_admin': True,
            'created_at': datetime.now().isoformat()
        }
        save_users(users)

def get_complaint_stats(complaints, user_email=None, is_admin=False):
    """Calculate complaint statistics"""
    if user_email and not is_admin:
        complaints = [c for c in complaints if c['user_email'] == user_email]
    
    total = len(complaints)
    pending = len([c for c in complaints if c['status'] in ['Filed', 'Under Review', 'In Progress']])
    resolved = len([c for c in complaints if c['status'] == 'Resolved'])
    
    return total, pending, resolved

def get_status_badge(status):
    """Return HTML badge for status"""
    status_class = status.lower().replace(' ', '-')
    return f'<span class="status-badge status-{status_class}">{status}</span>'

# Page Functions
def show_header():
    """Display main header"""
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ E-Complaint Justice Tracking System</h1>
        <p>Transparent • Efficient • Accountable</p>
    </div>
    """, unsafe_allow_html=True)

def login_page():
    """Login page"""
    show_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 Login")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                users = load_users()
                user = users.get(email)
                
                if user and user['password'] == hash_password(password):
                    st.session_state.current_user = user
                    st.session_state.page = 'dashboard'
                    st.success(f"✓ Welcome, {user['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password!")
        
        st.markdown("---")
        if st.button("Don't have an account? Register here", use_container_width=True):
            st.session_state.page = 'register'
            st.rerun()
        
        st.info("**Demo Admin:** admin@justice.gov / admin123")

def register_page():
    """Registration page"""
    show_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("📝 Register New Account")
        
        with st.form("register_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register", use_container_width=True)
            
            if submit:
                if not all([name, email, phone, password, confirm_password]):
                    st.error("❌ All fields are required!")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match!")
                else:
                    users = load_users()
                    if email in users:
                        st.error("❌ Email already registered!")
                    else:
                        users[email] = {
                            'name': name,
                            'email': email,
                            'phone': phone,
                            'password': hash_password(password),
                            'is_admin': False,
                            'created_at': datetime.now().isoformat()
                        }
                        save_users(users)
                        st.success("✓ Registration successful! Please login.")
                        st.session_state.page = 'login'
                        st.rerun()
        
        st.markdown("---")
        if st.button("Already have an account? Login here", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()

def dashboard_page():
    """Dashboard page"""
    show_header()
    user = st.session_state.current_user
    
    st.title(f"Welcome, {user['name']}! 👋")
    
    complaints = load_complaints()
    total, pending, resolved = get_complaint_stats(
        complaints, 
        user['email'], 
        user['is_admin']
    )
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{total}</h2>
            <p>Total Complaints</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{pending}</h2>
            <p>Pending</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{resolved}</h2>
            <p>Resolved</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.subheader("Quick Actions")
    
    if user['is_admin']:
        if st.button("📋 Manage All Complaints", use_container_width=True):
            st.session_state.page = 'admin_dashboard'
            st.rerun()
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 File New Complaint", use_container_width=True):
                st.session_state.page = 'file_complaint'
                st.rerun()
        with col2:
            if st.button("📋 View My Complaints", use_container_width=True):
                st.session_state.page = 'my_complaints'
                st.rerun()

def file_complaint_page():
    """File complaint page"""
    show_header()
    
    st.title("📄 File a New Complaint")
    
    with st.form("complaint_form"):
        title = st.text_input("Complaint Title")
        
        category = st.selectbox(
            "Category",
            ["", "Police", "Court", "Civic Body", "Corruption", "Public Services", "Other"]
        )
        
        description = st.text_area("Description", height=150)
        
        location = st.text_input("Location")
        
        incident_date = st.date_input("Incident Date", max_value=date.today())
        
        evidence_file = st.file_uploader(
            "Upload Evidence (Photo/Document)",
            type=['png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx']
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Submit Complaint", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.page = 'dashboard'
            st.rerun()
        
        if submit:
            if not all([title, category, description, location]):
                st.error("❌ Please fill all required fields!")
            else:
                complaints = load_complaints()
                complaint_id = len(complaints) + 1
                
                evidence_filename = None
                if evidence_file:
                    evidence_filename = f"{complaint_id}_{evidence_file.name}"
                    with open(UPLOAD_DIR / evidence_filename, 'wb') as f:
                        f.write(evidence_file.getbuffer())
                
                new_complaint = {
                    'id': complaint_id,
                    'user_email': st.session_state.current_user['email'],
                    'user_name': st.session_state.current_user['name'],
                    'title': title,
                    'category': category,
                    'description': description,
                    'location': location,
                    'incident_date': incident_date.isoformat(),
                    'evidence_file': evidence_filename,
                    'status': 'Filed',
                    'department': None,
                    'admin_notes': None,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                complaints.append(new_complaint)
                save_complaints(complaints)
                
                st.success(f"✓ Complaint #{complaint_id} filed successfully!")
                st.session_state.page = 'my_complaints'
                st.rerun()

def my_complaints_page():
    """User's complaints page"""
    show_header()
    
    st.title("📋 My Complaints")
    
    complaints = load_complaints()
    user_complaints = [c for c in complaints if c['user_email'] == st.session_state.current_user['email']]
    
    if not user_complaints:
        st.info("You haven't filed any complaints yet.")
        if st.button("File Your First Complaint"):
            st.session_state.page = 'file_complaint'
            st.rerun()
    else:
        for complaint in sorted(user_complaints, key=lambda x: x['created_at'], reverse=True):
            with st.container():
                st.markdown(f"""
                <div class="complaint-card">
                    <h3>#{complaint['id']} - {complaint['title']}</h3>
                    <p><strong>Category:</strong> {complaint['category']} {get_status_badge(complaint['status'])}</p>
                    <p><strong>Location:</strong> {complaint['location']}</p>
                    <p><strong>Filed Date:</strong> {datetime.fromisoformat(complaint['created_at']).strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View Details #{complaint['id']}", key=f"view_{complaint['id']}"):
                    st.session_state.selected_complaint = complaint['id']
                    st.session_state.page = 'view_complaint'
                    st.rerun()
                
                st.markdown("---")

def view_complaint_page():
    """View complaint details"""
    show_header()
    
    st.title("📄 Complaint Details")
    
    complaints = load_complaints()
    complaint = next((c for c in complaints if c['id'] == st.session_state.selected_complaint), None)
    
    if not complaint:
        st.error("Complaint not found!")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(complaint['title'])
        st.markdown(f"**Complaint ID:** #{complaint['id']}")
        st.markdown(f"**Category:** {complaint['category']}")
        st.markdown(f"**Status:** {get_status_badge(complaint['status'])}", unsafe_allow_html=True)
        st.markdown(f"**Location:** {complaint['location']}")
        st.markdown(f"**Incident Date:** {complaint['incident_date']}")
        st.markdown(f"**Filed Date:** {datetime.fromisoformat(complaint['created_at']).strftime('%Y-%m-%d %H:%M')}")
        
        if complaint['department']:
            st.markdown(f"**Assigned Department:** {complaint['department']}")
    
    st.markdown("---")
    
    st.subheader("Description")
    st.write(complaint['description'])
    
    if complaint['evidence_file']:
        st.markdown(f"**Evidence File:** {complaint['evidence_file']}")
    
    if complaint['admin_notes']:
        st.markdown("---")
        st.subheader("Admin Notes")
        st.info(complaint['admin_notes'])
    
    if st.button("← Back to My Complaints"):
        st.session_state.page = 'my_complaints'
        st.rerun()

def admin_dashboard_page():
    """Admin dashboard"""
    show_header()
    
    st.title("🏛️ Admin Dashboard")
    
    complaints = load_complaints()
    total = len(complaints)
    filed = len([c for c in complaints if c['status'] == 'Filed'])
    in_progress = len([c for c in complaints if c['status'] == 'In Progress'])
    resolved = len([c for c in complaints if c['status'] == 'Resolved'])
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{total}</h2>
            <p>Total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{filed}</h2>
            <p>Filed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{in_progress}</h2>
            <p>In Progress</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{resolved}</h2>
            <p>Resolved</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("All Complaints")
    
    if not complaints:
        st.info("No complaints in the system.")
    else:
        for complaint in sorted(complaints, key=lambda x: x['created_at'], reverse=True):
            with st.container():
                st.markdown(f"""
                <div class="complaint-card">
                    <h3>#{complaint['id']} - {complaint['title']}</h3>
                    <p><strong>Filed by:</strong> {complaint['user_name']} | <strong>Category:</strong> {complaint['category']} {get_status_badge(complaint['status'])}</p>
                    <p><strong>Location:</strong> {complaint['location']} | <strong>Date:</strong> {datetime.fromisoformat(complaint['created_at']).strftime('%Y-%m-%d')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Manage #{complaint['id']}", key=f"manage_{complaint['id']}"):
                    st.session_state.selected_complaint = complaint['id']
                    st.session_state.page = 'manage_complaint'
                    st.rerun()
                
                st.markdown("---")

def manage_complaint_page():
    """Manage complaint (admin)"""
    show_header()
    
    st.title("⚙️ Manage Complaint")
    
    complaints = load_complaints()
    complaint = next((c for c in complaints if c['id'] == st.session_state.selected_complaint), None)
    
    if not complaint:
        st.error("Complaint not found!")
        return
    
    # Display complaint details
    st.subheader("Complaint Details")
    st.markdown(f"""
    <div class="complaint-card">
        <h3>{complaint['title']}</h3>
        <p><strong>ID:</strong> #{complaint['id']}</p>
        <p><strong>Filed by:</strong> {complaint['user_name']}</p>
        <p><strong>Category:</strong> {complaint['category']}</p>
        <p><strong>Location:</strong> {complaint['location']}</p>
        <p><strong>Incident Date:</strong> {complaint['incident_date']}</p>
        <p><strong>Description:</strong> {complaint['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Update Complaint")
    
    with st.form("update_form"):
        status = st.selectbox(
            "Status",
            ["Filed", "Under Review", "In Progress", "Resolved", "Rejected"],
            index=["Filed", "Under Review", "In Progress", "Resolved", "Rejected"].index(complaint['status'])
        )
        
        department = st.selectbox(
            "Assign Department",
            ["", "Police Department", "Court Services", "Civic Services", "Anti-Corruption Bureau"],
            index=0 if not complaint['department'] else 
                  ["", "Police Department", "Court Services", "Civic Services", "Anti-Corruption Bureau"].index(complaint['department'])
        )
        
        admin_notes = st.text_area("Admin Notes", value=complaint['admin_notes'] or "", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Update Complaint", use_container_width=True)
        with col2:
            back = st.form_submit_button("Back to Dashboard", use_container_width=True)
        
        if back:
            st.session_state.page = 'admin_dashboard'
            st.rerun()
        
        if submit:
            # Update complaint
            for i, c in enumerate(complaints):
                if c['id'] == complaint['id']:
                    complaints[i]['status'] = status
                    complaints[i]['department'] = department if department else None
                    complaints[i]['admin_notes'] = admin_notes if admin_notes else None
                    complaints[i]['updated_at'] = datetime.now().isoformat()
                    break
            
            save_complaints(complaints)
            st.success("✓ Complaint updated successfully!")
            st.session_state.page = 'admin_dashboard'
            st.rerun()

# Sidebar Navigation
def sidebar():
    """Sidebar navigation"""
    with st.sidebar:
        st.title("Navigation")
        
        if st.session_state.current_user:
            user = st.session_state.current_user
            st.success(f"Logged in as:\n**{user['name']}**")
            
            st.markdown("---")
            
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.page = 'dashboard'
                st.rerun()
            
            if user['is_admin']:
                if st.button("🏛️ Admin Panel", use_container_width=True):
                    st.session_state.page = 'admin_dashboard'
                    st.rerun()
            else:
                if st.button("📄 File Complaint", use_container_width=True):
                    st.session_state.page = 'file_complaint'
                    st.rerun()
                
                if st.button("📋 My Complaints", use_container_width=True):
                    st.session_state.page = 'my_complaints'
                    st.rerun()
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.current_user = None
                st.session_state.page = 'login'
                st.rerun()

# Main Application
def main():
    """Main application"""
    init_system()
    
    # Show sidebar if logged in
    if st.session_state.current_user:
        sidebar()
    
    # Route to appropriate page
    page = st.session_state.page
    
    if page == 'login':
        login_page()
    elif page == 'register':
        register_page()
    elif page == 'dashboard':
        dashboard_page()
    elif page == 'file_complaint':
        file_complaint_page()
    elif page == 'my_complaints':
        my_complaints_page()
    elif page == 'view_complaint':
        view_complaint_page()
    elif page == 'admin_dashboard':
        admin_dashboard_page()
    elif page == 'manage_complaint':
        manage_complaint_page()

if __name__ == "__main__":
    main()