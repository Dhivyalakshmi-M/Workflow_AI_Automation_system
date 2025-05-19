import streamlit as st
import pandas as pd
import pywhatkit as pwk
import time
from datetime import datetime, timedelta
import hashlib

# Initialize employees_db in session state if it doesn't exist
if 'employees_db' not in st.session_state:
    st.session_state.employees_db = {
        'emp_data': pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005', 'EMP006', 'EMP007', 'EMP008'],
            'name': ['LakshmiPriya', 'Nikitha', 'Muruganandam', 'TamilSelvan', 'Sashmitha', 'Sarvesh', 'Kalaiselvi', 'Suriya'],
            'position': ['Senior Developer', 'Junior Developer', 'UI/UX Designer', 'Graphic Designer', 'Project Manager', 'QA Engineer', 'DevOps Specialist', 'Senior Developer'],
            'department': ['Engineering', 'Engineering', 'Design', 'Design', 'Management', 'Engineering', 'Operations', 'Engineering'],
            'phone': ['+916379739458', '+919629012589', '+916379739458', '+919629012589', '+919344096003', '+916379739458', '+919629012589','+916379739458'],
            'email': ['LakshmiPriya@company.com', 'Nikitha@company.com', 'Muruganandam@company.com', 'Tamil Selvan@company.com', 'Sashmitha@company.com', 'Sarvesh@company.com', 'Kalaiselvi@company.com', 'Suriya@company.com'],
            'password_hash': [hashlib.sha256(pw.encode()).hexdigest() for pw in ['1', 'password2', 'password3', 'password4', 'password5', 'password6', 'password7', '8']],
            'current_workload': [3, 2, 4, 1, 2, 3, 2, 2],
            'skills': ['Python, Django, SQL', 'JavaScript, React, Node.js', 'Figma, Adobe XD, Photoshop', 'Illustrator, InDesign, Photography', 'Agile, Scrum, Project Planning', 'Testing, Automation, Selenium', 'AWS, Docker, Kubernetes', 'Python, Java, Cloud Architecture'],
            'can_cover': ['Senior Developer, Tech Lead', 'Junior Developer, Frontend Developer', 'UI/UX Designer, Product Designer', 'Graphic Designer, Visual Designer', 'Project Manager, Product Owner', 'QA Engineer, Test Engineer', 'DevOps Specialist, Cloud Engineer', 'Senior Developer, Architect']
        }),
        'leave_requests': pd.DataFrame(columns=[
            'request_id', 'employee_id', 'employee_name', 'position', 'department',
            'leave_start', 'leave_end', 'reason', 'status', 'assigned_to', 
            'assigned_to_name', 'assigned_to_phone', 'work_details', 'phone', 'email', 'submission_date'
        ])
    }

# Make employees_db available globally
employees_db = st.session_state.employees_db

# ------------------------- Helper Functions -------------------------
def generate_request_id():
    return f"REQ{int(time.time()) % 1000000}"

def send_whatsapp_message_instant(phone_number, message):
    """Send WhatsApp message instantly without waiting"""
    try:
        pwk.sendwhatmsg_instantly(
            phone_no=phone_number,
            message=message,
            tab_close=True,
            close_time=3
        )
        return True
    except Exception as e:
        error_msg = f"""
        ⚠️ WhatsApp Notification Failed
        
        Please ensure:
        1. WhatsApp Web is open in your default browser
        2. You're logged in to WhatsApp Web
        3. Your internet connection is stable
        
        Technical Details: {str(e)}
        """
        st.error(error_msg)
        return False

def get_available_employee(employee_position, employee_department, exclude_id=None):
    """Enhanced employee matching with flexible coverage options"""
    df = employees_db['emp_data']
    
    # First try: Exact position match in same department
    candidates = df[
        (df['position'] == employee_position) & 
        (df['department'] == employee_department) & 
        (df['employee_id'] != exclude_id) &
        (df['current_workload'] < 5)
    ]
    
    if not candidates.empty:
        return candidates.loc[candidates['current_workload'].idxmin()]
    
    # Second try: Employees who list this position in their can_cover list
    flexible_candidates = df[
        df['can_cover'].str.contains(employee_position) &
        (df['employee_id'] != exclude_id) &
        (df['current_workload'] < 5)
    ]
    
    if not flexible_candidates.empty:
        return flexible_candidates.loc[flexible_candidates['current_workload'].idxmin()]
    
    # Third try: Same department, different position but similar skills
    department_candidates = df[
        (df['department'] == employee_department) & 
        (df['employee_id'] != exclude_id) &
        (df['current_workload'] < 5)
    ]
    
    if not department_candidates.empty:
        return department_candidates.loc[department_candidates['current_workload'].idxmin()]
    
    return None

def assign_work(leave_request):
    """Enhanced work assignment with immediate feedback"""
    global employees_db
    
    try:
        position = leave_request['position']
        department = leave_request['department']
        exclude_id = leave_request['employee_id']
        
        assigned_emp = get_available_employee(position, department, exclude_id)
        
        if assigned_emp is not None and not assigned_emp.empty:
            # Generate work assignment details
            work_details = f"""
            📌 Work Assignment Details
            
            Task: Cover for {leave_request['employee_name']}'s leave
            Period: {leave_request['leave_start']} to {leave_request['leave_end']}
            Reason: {leave_request['reason']}
            
            Priority: Medium
            Expected Deliverables:
            "1. Review all pending pull requests (5 minimum)",
            "2. Attend daily FinTech standup meetings",
            "3. Prepare weekly client status report",
            "4. Verify production deployment checklist",
            "5. Conduct code review session with juniors",
            "6. Update project documentation",
            "7. Monitor system performance metrics",
            "8. Resolve critical priority bugs",
            "9. Prepare client demo materials",
            "10. Complete handover documentation"
            """
            
            # Create new request
            new_request = {
                'request_id': generate_request_id(),
                **leave_request,
                'status': 'Assigned',
                'assigned_to': assigned_emp['employee_id'],
                'assigned_to_name': assigned_emp['name'],
                'assigned_to_phone': assigned_emp['phone'],
                'work_details': work_details,
                'submission_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Added seconds for more precision
            }
            
            # Update database - ensure we're modifying the actual DataFrame
            new_df = pd.DataFrame([new_request])
            employees_db['leave_requests'] = pd.concat(
                [employees_db['leave_requests'], new_df],
                ignore_index=True
            )
            
            # Update workload - use .loc for proper assignment
            mask = employees_db['emp_data']['employee_id'] == assigned_emp['employee_id']
            employees_db['emp_data'].loc[mask, 'current_workload'] += 1
            
            # Force update session state
            st.session_state.employees_db = employees_db

            # Prepare messages
            assigned_msg = f"""🚀 New Work Assignment 🚀

You have been assigned to cover {leave_request['employee_name']}'s responsibilities:

{work_details}

Please acknowledge receipt of this assignment.
"""
            
            leave_taker_msg = f"""✅ Leave Request Approved ✅

Dear {leave_request['employee_name']},

Your leave from {leave_request['leave_start']} to {leave_request['leave_end']} has been approved.

Your work will be covered by:
{assigned_emp['name']} ({assigned_emp['position']})
Contact: {assigned_emp['phone']}

Please coordinate handover before your leave.
"""
            
            # Send messages and get status
            msg_status = {
                'assigned': send_whatsapp_message_instant(assigned_emp['phone'], assigned_msg),
                'leave_taker': send_whatsapp_message_instant(leave_request['phone'], leave_taker_msg)
            }
            
            # Prepare success message
            success_msg = f"""
            ✅ Leave request submitted successfully!
            
            • Assigned to: {assigned_emp['name']}
            • Period: {leave_request['leave_start']} to {leave_request['leave_end']}
            • WhatsApp Status: {'All sent' if all(msg_status.values()) else 'Partial success'}
            """
            
            # Store message in session state to persist across reruns
            st.session_state.last_assignment_msg = {
                'message': success_msg,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            
            return True, work_details, all(msg_status.values())
        
        return False, None, False
        
    except Exception as e:
        st.error(f"Assignment error: {str(e)}")
        return False, None, False

def authenticate(employee_id, password):
    """Secure authentication"""
    df = employees_db['emp_data']
    employee = df[df['employee_id'] == employee_id]
    
    if not employee.empty:
        stored_hash = employee.iloc[0]['password_hash']
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        return input_hash == stored_hash
    return False


# ------------------------- Streamlit UI -------------------------
def set_page_config():
    """Modern page configuration with vibrant gradient"""
    st.set_page_config(
        page_title="WorkFlow Automator Pro",
        page_icon="🤖",
        #layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Vibrant gradient background
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #43cea2 0%, #185a9d 100%);
        color: #ffffff;
    }
    .stTextInput>div>div>input, .stDateInput>div>div>input, 
    .stTextArea>div>div>textarea, .stSelectbox>div>div>select {
        background-color: rgba(255,255,255,0.95) !important;
        color: #333333 !important;
        border-radius: 8px;
    }
    .css-1aumxhk {
        background-color: rgba(255,255,255,0.15) !important;
        border-radius: 12px;
        padding: 25px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    .stButton>button {
        background-color: #FF6B6B;
        color: white;
        border-radius: 8px;
        padding: 12px 28px;
        border: none;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF8E8E;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .notification {
        background-color: rgba(255,255,255,0.2);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #FF6B6B;
    }
    .assignment-card {
        background-color: rgba(255,255,255,0.25);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #4ECDC4;
    }
    </style>
    """, unsafe_allow_html=True)

def login_page():
    """Enhanced login page with beautiful design"""

    
    # Custom CSS for the login page
    st.markdown("""
    <style>
    .login-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        max-width:700px;
        margin: 0 auto;
    }
    .login-header {
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .login-header h1 {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .login-header p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    .stTextInput>div>div>input {
        background-color: rgba(255,255,255,0.9) !important;
        border-radius: 10px !important;
        padding: 12px 15px !important;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px !important;
        padding: 12px !important;
        font-weight: bold !important;
        background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%) !important;
        border: none !important;
        font-size: 1rem !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
    }
    .error-message {
        color: #ff6b6b;
        text-align: center;
        margin-top: 15px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main login container
    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <h1>🔐 WorkFlow Automation AI Pro</h1>
            <p>Intelligent Workforce Management Platform</p>
        </div>
    """, unsafe_allow_html=True)

    # Login form
    with st.form("login_form"):
        
        emp_id = st.text_input("Employee ID", 
                              placeholder="Enter your EMP ID (e.g. EMP001)",
                              key="emp_id_input")
        
        password = st.text_input("Password", 
                                type="password", 
                                placeholder="Enter your password",
                                key="password_input")
        
        submitted = st.form_submit_button("Employee Work Portal – Sign In", 
                                        type="primary",
                                        use_container_width=True)
        
        if submitted:
            if authenticate(emp_id, password):
                st.session_state['logged_in'] = True
                st.session_state['employee_id'] = emp_id
                employee = employees_db['emp_data'][employees_db['emp_data']['employee_id'] == emp_id].iloc[0]
                st.session_state.update({
                    'employee_name': employee['name'],
                    'position': employee['position'],
                    'department': employee['department'],
                    'phone': employee['phone'],
                    'email': employee['email'],
                    'skills': employee['skills']
                })
                st.rerun()
            else:
                st.markdown("""
                <div class="error-message">
                    ❌ Invalid credentials. Please try again.
                </div>
                """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 30px; color: white; opacity: 0.7;">
        <p>Need help? Contact IT Support at support@workflowai.com</p>
        <p>© 2023 WorkFlow AI Pro. All rights reserved.</p>
    </div>
    </div>
    """, unsafe_allow_html=True)

       
def dashboard():
    """Modern dashboard with rich content"""
    employee = {k: st.session_state[k] for k in [
        'employee_id', 'employee_name', 'position',
        'department', 'phone','email', 'skills'
    ]}
            # Logout button

    # Header with user profile
    col1, col2 = st.columns([1,4])
    with col1:
        st.image("https://ui-avatars.com/api/?name=" + employee['employee_name'] + "&background=random&size=150",
                 width=130)
    with col2:
        st.title(f"👋 Welcome, {employee['employee_name']}")
        st.markdown(f"""
        **{employee['position']}** | {employee['department']} Department
        📱 {employee['phone']} | ✉️ {employee['email']}
        🛠️ Skills: {employee['skills']}
        """)

    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["🏖️ Request Leave", "📋 My Assignments", "📊 Leave Status"])

    # In your leave request submission section (tab1):
    with tab1:
        st.header("New Leave Request")
        with st.form("leave_form", clear_on_submit=True):
            
            cols = st.columns(2)
            with cols[0]:
                leave_start = st.date_input("Start Date", min_value=datetime.today())
            with cols[1]:
                leave_end = st.date_input("End Date", min_value=datetime.today())

            reason = st.text_area("Reason for Leave",
                                        placeholder="Briefly explain the reason for your leave (min. 20 characters)",
                                        height=100)
            
            submitted = st.form_submit_button("Submit Leave Request", type="primary")
            
            if submitted:
                if leave_end < leave_start:
                    st.error("End date must be after start date")
                elif len(reason) < 20:
                    st.error("Please provide a more detailed reason (at least 20 characters)")
                else:
                
                    with st.spinner("Processing your request..."):
                        new_request = {
                            'employee_id': employee['employee_id'],
                            'employee_name': employee['employee_name'],
                            'position': employee['position'],
                            'department': employee['department'],
                            'leave_start': leave_start.strftime('%Y-%m-%d'),
                            'leave_end': leave_end.strftime('%Y-%m-%d'),
                            'reason': reason,
                            'status': 'Pending',
                            'assigned_to': None,
                            'assigned_to_name': None,
                            'work_details': None,
                            'phone': employee['phone'],
                            'email': employee['email']
                        }
                    
                    success, work_details, messages_sent = assign_work(new_request)
                    
                    # Display any stored success message
                    if 'last_assignment_msg' in st.session_state:
                        msg = st.session_state.last_assignment_msg
                        if (datetime.now() - datetime.strptime(msg['timestamp'], '%H:%M:%S')).seconds < 10:
                            st.success(msg['message'])
                            st.balloons()
                    
                    if not success:
                        st.warning("""
                        ⚠️ Leave submitted but no available cover found
                        
                        Your leave request has been recorded but we couldn't
                        automatically assign your work to another team member.
                        Please contact your manager.
                        """)
        
        # Clear the message after displaying
        if 'last_assignment_msg' in st.session_state:
            del st.session_state.last_assignment_msg
        st.markdown("---")
        if st.button("🚪 Logout", type="primary", key="logout_tab1"):  # Added unique key
            st.session_state.clear()
            st.rerun()

        # In your dashboard tab2 section:
    with tab2:
        st.header("📋 My Assignments")
        
        # Initialize sample assignment if none exist
        if len(st.session_state.employees_db['leave_requests']) == 0:
            work_details = """📌 Work Assignment Details

    Task: Cover for Lakshmi Priya's Senior Developer responsibilities
    Period: {start_date} to {end_date}
    Reason: Annual vacation leave

    Priority: High
    Reporting To: Sashmitha (Project Manager)

    📝 Key Responsibilities:
    1. Code Quality Assurance:
       - Review all pull requests (avg. 5/day)
       - Maintain 90%+ test coverage
       - Conduct bi-weekly code reviews

    2. Client Communication:
       - Daily standups with FinTech client (10:30 AM)
       - Weekly status reports every Friday
       - Emergency contact for P1 issues

    3. Project Management:
       - Update Jira tickets daily
       - Monitor CI/CD pipeline
       - Verify production deployments

    4. Team Leadership:
       - Mentor junior developers
       - Conduct knowledge sharing sessions
       - Resolve technical blockers

    ⏳ Expected Time Commitment: 
    - Core Hours: 10:00 AM - 6:00 PM
    - Critical On-Call: Weekdays until 9:00 PM

    📂 Important Resources:
    - Project Docs: https://company.com/projects/fintech
    - Code Repository: https://github.com/company/fintech
    - Client Contacts: Listed in shared drive

    """.format(
        start_date=(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        end_date=(datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    )

            emp001_leave = {
                'request_id': 'REQ001',
                'employee_id': 'EMP001',
                'employee_name': 'Lakshmi Priya',
                'position': 'Senior Developer',
                'department': 'Engineering',
                'leave_start': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'leave_end': (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
                'reason': 'Annual vacation leave',
                'status': 'Assigned',
                'assigned_to': 'EMP008',
                'assigned_to_name': 'Suriya',
                'assigned_to_phone': '+916379739458',
                'work_details': work_details,
                'tasks': [
                        "1. Review all pending pull requests (5 minimum)",
                        "2. Attend daily FinTech standup meetings",
                        "3. Prepare weekly client status report",
                        "4. Verify production deployment checklist",
                        "5. Conduct code review session with juniors",
                        "6. Update project documentation",
                        "7. Monitor system performance metrics",
                        "8. Resolve critical priority bugs",
                        "9. Prepare client demo materials",
                        "10. Complete handover documentation"
                ],
                'completed_tasks': [],
                'phone': '+916379739458',
                'email': 'john@company.com',
                'submission_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Convert to DataFrame and add to leave_requests
            new_df = pd.DataFrame([emp001_leave])
            st.session_state.employees_db['leave_requests'] = pd.concat(
                [st.session_state.employees_db['leave_requests'], new_df],
                ignore_index=True
            )

        # Get current assignments
        current_emp_id = st.session_state.get('employee_id', '')
        assignments = st.session_state.employees_db['leave_requests'][
            (st.session_state.employees_db['leave_requests']['assigned_to'] == current_emp_id) & 
            (st.session_state.employees_db['leave_requests']['status'] == 'Assigned')
        ]

        if not assignments.empty:
            for _, assignment in assignments.iterrows():
                # Create task checkboxes
                st.markdown(f"### 🧑💼 Covering {assignment['employee_name']}'s Leave")
                
                # Convert tasks to list if stored as string
                tasks = assignment['tasks'] if isinstance(assignment['tasks'], list) else eval(assignment['tasks'])
                completed_tasks = assignment['completed_tasks'] if isinstance(assignment['completed_tasks'], list) else eval(assignment['completed_tasks'] or '[]')
                
                # Display progress
                progress = len(completed_tasks)/len(tasks) if tasks else 0
                st.progress(progress)
                st.caption(f"Completed {len(completed_tasks)} of {len(tasks)} tasks")
                
                # Display work details
                with st.expander("📋 Assignment Details"):
                    st.markdown(assignment['work_details'])
                    
                    st.markdown("### ✅ Task Completion")
                    updated_completed = completed_tasks.copy()
                    
                    for task in tasks:
                        is_completed = task in completed_tasks
                        if st.checkbox(
                            task,
                            value=is_completed,
                            key=f"task_{assignment['request_id']}_{task[:20]}"
                        ):
                            if task not in updated_completed:
                                updated_completed.append(task)
                        elif not is_completed and task in updated_completed:
                            updated_completed.remove(task)
                    
                    # Update completed tasks in session state
                    idx = st.session_state.employees_db['leave_requests'][
                        st.session_state.employees_db['leave_requests']['request_id'] == assignment['request_id']
                    ].index[0]
                    
                    st.session_state.employees_db['leave_requests'].at[idx, 'completed_tasks'] = str(updated_completed)
                    
                    # Complete assignment button
                    if len(updated_completed) == len(tasks):
                        if st.button("✅ Mark Assignment Complete", key=f"complete_{assignment['request_id']}"):
                            # Update status
                            st.session_state.employees_db['leave_requests'].at[idx, 'status'] = 'Completed'
                            
                            # Send WhatsApp notification
                            completion_msg = f"""✅ Assignment Completed

    Dear {assignment['employee_name']},

    Your work coverage has been successfully completed by {assignment['assigned_to_name']}.

    All tasks were finished:
    {chr(10).join(['• ' + t for t in tasks])}

    Looking forward to your return!
    """
                            send_whatsapp_message_instant(assignment['phone'], completion_msg)
                            
                            st.success("Assignment completed! Notification sent.")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.warning(f"Complete all {len(tasks)-len(updated_completed)} remaining tasks to finish")
                    
                    st.markdown("### 📞 Contact Information")
                    st.write(f"**{assignment['employee_name']}** (Original Worker)")
                    st.write(f"📱 {assignment['phone']} | ✉️ {assignment['email']}")
        
        else:
            st.info("You currently have no active assignments")
        
        if st.button("🔄 Refresh"):
            st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", type="primary", key="logout_tab2"):  # Added unique key
            st.session_state.clear()
            st.rerun()
                
        with tab3:
            st.header("Your Leave History")

            # Safely get leave history for current employee
            try:
                my_leaves = employees_db['leave_requests'][
                    employees_db['leave_requests']['employee_id'] == st.session_state['employee_id']
                ].sort_values('leave_start', ascending=False).copy()
            except KeyError as e:
                st.error(f"Error accessing leave history: {e}")
                my_leaves = pd.DataFrame()

            if not my_leaves.empty:
                for _, leave in my_leaves.iterrows():
                    status_color = {
                        'Pending': '#FFA500',
                        'Assigned': '#4ECDC4',
                        'Completed': '#185a9d',
                        'Rejected': '#FF6B6B'
                    }.get(leave['status'], '#888888')

                    # Create card for each leave entry
                    with st.container():
                        st.markdown(f"""
                        <div style="background-color: rgba(255,255,255,0.1);
                                        border-radius: 10px;
                                        padding: 15px;
                                        margin-bottom: 15px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <h4 style="margin:0;">Leave from {leave['leave_start']} to {leave['leave_end']}</h4>
                                <span style="color:{status_color}; font-weight:bold;">{leave['status']}</span>
                            </div>
                            <p><strong>Submitted on:</strong> {leave['submission_date']}</p>
                            <p><strong>Reason:</strong> {leave['reason']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Show coverage details if assigned
                        if pd.notna(leave.get('assigned_to_name', None)):
                            st.markdown("---")
                            st.subheader("Coverage Arrangement")

                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.write(f"**Assigned to:** {leave['assigned_to_name']}")
                                if 'assigned_to_phone' in leave:
                                    st.write(f"**Contact:** {leave['assigned_to_phone']}")

                            with col2:
                                if st.button("View Work Details", key=f"details_{leave['request_id']}"):
                                    st.markdown(f"""
                                    <div style="background-color: rgba(255,255,255,0.05);
                                                        padding: 15px;
                                                        border-radius: 8px;
                                                        margin-top: 10px;">
                                            {leave.get('work_details', 'No details available').replace('\n', '<br>')}
                                    </div>
                                    """, unsafe_allow_html=True)

                        st.markdown("---")
            else:
                st.info("""
                No leave requests found in your history.

                Submit a leave request using the 'Request Leave' tab to get started.
                """)
            st.markdown("---")
            if st.button("🚪 Logout", type="primary", key="logout_tab3"):  # Added unique key
                st.session_state.clear()
                st.rerun()
            
# ------------------------- Main App -------------------------
def main():
    set_page_config()
    
    if 'logged_in' not in st.session_state:
        login_page()
    else:
        dashboard()

if __name__ == "__main__":
    main()



