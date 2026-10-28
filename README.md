# Visitor Access Management System (VAMS)

A Django-based web application designed to digitize student visitor access requests and visitor card management at Menara Batavia.

## Overview

The Visitor Access Management System (VAMS) streamlines the visitor access process by allowing students to submit access requests online while enabling security officers to review requests, issue visitor cards, and record card returns.

The system also provides administrators with tools to manage system records and monitor visitor card transactions.

## Key Features

- **Role-Based Access Control** — Separate access for Students, Security Officers, and Administrators.
- **Student Registration and Login** — Manage user authentication and student accounts.
- **Access Request Management** — Allow students to submit visitor access requests.
- **Request Approval Workflow** — Enable security officers to approve or reject access requests.
- **Visitor Card Management** — Track card availability, issuance, and returns.
- **Transaction History** — Maintain records of borrowing and return activities.
- **Staff Activity Tracking** — Record which staff members review requests, issue cards, and receive returned cards.
- **Overdue Monitoring** — Support monitoring of overdue visitor card transactions.
- **Administrative Dashboard** — Provide tools for system and transaction management.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Programming language |
| Django | Web application framework |
| SQLite | Local development database |
| HTML and CSS | Frontend structure and styling |
| Django Templates | Server-side page rendering |
| Git and GitHub | Version control and source code hosting |

## User Roles

| Role | Responsibilities |
|---|---|
| Student | Register, log in, manage profile information, and submit access requests |
| Security Officer | Review access requests and manage visitor card issuance and returns |
| Administrator | Manage system records and review transaction history |

## Project Structure

```text
visitor-access-management-system/
├── accounts/          # User accounts, authentication, and roles
├── access_requests/   # Visitor access request workflow
├── visitor_cards/     # Visitor cards and transaction management
├── config/            # Django project configuration
├── templates/         # HTML templates
├── static/            # Static assets such as CSS
├── manage.py          # Django management utility
├── requirements.txt   # Python dependencies
├── .env.example       # Example environment configuration
├── .gitignore         # Files excluded from Git
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.12 or a compatible Python version
- Git
- pip

### 1. Clone the repository

```bash
git clone https://github.com/cristchaw/visitor-access-management-system.git
cd visitor-access-management-system
```

### 2. Create a virtual environment

Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using `.env.example` as a reference.

```bash
cp .env.example .env
```

Replace the placeholder secret key in `.env` with a newly generated development secret key. Never commit the real `.env` file.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Create an administrator account

```bash
python manage.py createsuperuser
```

Follow the prompts to create your local administrator account.

### 7. Run the development server

```bash
python manage.py runserver
```

Open the local development address shown in the terminal, usually `http://127.0.0.1:8000/`.

## Security Notes

- Keep secret keys and credentials outside source control.
- Do not commit `.env` files, local databases, or personal data.
- Use environment variables to configure sensitive settings.
- `DEBUG` should be disabled in production.
- Configure production settings before deploying the application.

## Project Status

VAMS is under active development. Features, documentation, and system workflows may evolve as development continues.

## License

No license has been specified yet. All rights are reserved by default unless a license is added.
