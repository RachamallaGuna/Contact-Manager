# Contact Manager

A full-stack contact management platform with per-user accounts, CRUD contact
records, and cloud-backed profile image storage. Built to get real, working
experience with the kind of infrastructure decisions that don't show up in a
toy CRUD app — per-environment config, storage abstraction, and auth done
properly rather than skipped.

---

## Tech Stack

| Layer      | Technology                                    |
|------------|------------------------------------------------|
| Backend    | Python, Flask, Flask-SQLAlchemy, Flask-Login   |
| Auth       | Session-based, salted password hashing (Werkzeug) |
| Database   | MySQL (via PyMySQL) — SQLite fallback for local dev |
| Storage    | AWS S3 (via boto3) — local disk fallback for local dev |
| Frontend   | Jinja2 templates, Bootstrap 5                  |

## Features

- Account registration & login, one user's contacts are never visible to another
- Create, edit, delete, and search contacts by name
- Per-contact profile image upload, stored on S3 in production
- MySQL in production, SQLite fallback locally (auto-detected from env vars)

---

## Data Model

**`user`** — id, email (unique), password_hash

**`contact`** — id, name, email, phone, notes, profile_image_url, created_at, user_id (FK → user)

Tables are created automatically on startup via SQLAlchemy — no manual
migration step needed to get running.

---

## Running it

```bash
git clone <your-repo-url>
cd contact-app
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Open `http://127.0.0.1:5000`. No MySQL or AWS needed to try it — it just
uses SQLite and local storage until you configure the real thing.

## Config for MySQL + S3

```
SECRET_KEY=your-secret-key

DB_USER=your_mysql_user
DB_PASS=your_mysql_password
DB_HOST=your_mysql_host
DB_NAME=contacts_db

AWS_S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

## Project Structure

```
contact-app/
├── app/
│   ├── __init__.py     # app factory, DB/S3 config resolution
│   ├── models.py       # User, Contact
│   ├── auth.py         # register / login / logout
│   ├── contacts.py     # contact CRUD routes
│   ├── storage.py       # image upload — S3 or local, single call site
│   ├── templates/
│   └── static/uploads/
├── main.py
├── requirements.txt
└── README.md
```
## Possible Next Steps

- Contact tags/categories with filtering
- CSV export
- Pagination for large contact lists
- Unit tests for auth and CRUD routes
