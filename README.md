# Visitor Access Management System (VAMS)

A Django-based web application designed to streamline student visitor access requests and visitor card management.

## Overview

The Visitor Access Management System (VAMS) is a web application designed to support visitor access operations at Menara Batavia. It digitizes the access request and visitor card management process, helping staff monitor requests, manage card issuance and returns, and maintain transaction records.

## Key Features

- **Role-Based Access Control** — Separate access for Students, Security Officers, and Administrators.
- **Student Access Requests** — Students can submit visitor access requests.
- **Request Review** — Security Officers can approve or reject access requests.
- **Visitor Card Management** — Manage card availability, issuance, and returns.
- **Transaction Tracking** — Record borrowing deadlines, return times, and transaction statuses.
- **Staff Activity Tracking** — Track request reviewers, card issuance staff, and return recipients.
- **Overdue Monitoring** — Support monitoring of overdue card transactions.
- **Administrative Management** — Manage system records and review transaction history.

## Technology Stack

- **Backend:** Python, Django
- **Database:** SQLite for local development
- **Frontend:** Django Templates, HTML, CSS, Bootstrap
- **Version Control:** Git and GitHub

## Application Roles

| Role | Responsibilities |
|---|---|
| Student | Register, log in, and submit access requests |
| Security Officer | Review requests and manage card issuance and returns |
| Administrator | Manage system records and review transaction history |

## Project Structure

```text
accounts/          User accounts and roles
access_requests/   Visitor access request workflow
visitor_cards/     Visitor card and transaction management
config/            Django project configuration
templates/         HTML templates
static/            Static assets
manage.py          Django management utility
```

## Local Development Setup

### 1. Clone the repository

```bash
git clone <REPOSITORY_URL>
cd visitor-access-management-system
```

### 2. Create and activate a virtual environment

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Create an administrator account

```bash
python manage.py createsuperuser
```

Follow the prompts to create your local administrator account.

### 6. Start the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Security Notes

- Do not commit passwords, API keys, secret keys, or other credentials.
- Do not commit local database files or virtual environments.
- Use environment variables for sensitive configuration.
- Use production-appropriate settings before deploying the application.

## Project Status

The application is under active development. Features and documentation may evolve as development continues.

## License

See the [LICENSE](LICENSE) file for licensing information.
