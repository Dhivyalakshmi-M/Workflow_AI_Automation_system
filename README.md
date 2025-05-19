# WorkFlow Automation AI Pro 🤖

**WorkFlow Automation AI Pro** is an intelligent workforce management platform that automates leave requests and work assignments with WhatsApp integration for seamless team coordination.

## Features ✨

- **Modern UI**: Beautiful gradient-based interface with responsive design
- **Secure Authentication**: SHA-256 password hashing for employee login
- **Automated Work Assignment**: Smart algorithm matches leave-takers with available colleagues
- **WhatsApp Notifications**: Instant alerts for new assignments and status updates
- **Task Management**: Track progress on assigned work with completion checklists
- **Leave History**: View all past leave requests with status tracking
- **Employee Profiles**: Detailed team member information with skills tracking

## How It Works ⚙️

1. Employees submit leave requests through the portal
2. System automatically finds suitable coverage based on:
   - Position matching
   - Department alignment
   - Skills compatibility
   - Current workload
3. Both parties receive WhatsApp notifications
4. Coverage provider tracks tasks to completion
5. Original employee receives completion confirmation

## Installation 🛠️

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/workflow-automation-ai.git
   cd workflow-automation-ai
Install dependencies:

bash
pip install -r requirements.txt
Run the application:

bash
streamlit run app.py
Configuration ⚙️
Before running:

Ensure WhatsApp Web is open in your default browser

Be logged in to WhatsApp Web

Update employee data in app.py as needed

Usage Guide 📖
Employee Login
Use credentials from the initialized database

Sample IDs: EMP001 to EMP008

Sample passwords: "1" to "8" (for demo purposes)

Requesting Leave
Navigate to "Request Leave" tab

Select dates and provide reason

Submit - system will automatically arrange coverage

Managing Assignments
View active assignments in "My Assignments" tab

Mark tasks as complete

Finalize assignment when all tasks are done

Demo Credentials 👤
Employee ID	Name	Position	Password
EMP001	Lakshmi Priya	Senior Developer	1
EMP002	Nikitha	Junior Developer	2
EMP005	Sashmitha	Project Manager	5
Screenshots 📸
Login Page
Modern login interface

Dashboard
Employee dashboard with leave management

Contributing 🤝
Contributions are welcome! Please open an issue or submit a pull request.

License 📄
This project is licensed under the MIT License - see the LICENSE file for details.


---

### `requirements.txt`

```text
streamlit==1.28.0
pandas==2.0.3
pywhatkit==5.4
python-dotenv==1.0.0
hashlib==20081119
