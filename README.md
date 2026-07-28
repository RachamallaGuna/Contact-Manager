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

### A note on the fallbacks

Both the database and image storage are config-driven rather than
hardcoded: if `DB_*` environment variables aren't set, the app runs on
SQLite; if `AWS_S3_BUCKET` isn't set, uploaded images are written to local
disk instead. This means the exact same codebase runs with zero setup on a
laptop and with real MySQL + S3 in production — no code branches, no
"local version" of the app to maintain separately. See `app/storage.py` and
`app/__init__.py`.

---

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

## How to Run

### 1. Prerequisites

- Python 3.10+
- (Optional) MySQL running locally, with a database created
- (Optional) An AWS S3 bucket + IAM credentials, if you want real cloud image storage

### 2. Setup

```bash
git clone <your-repo-url>
cd contact-app
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Open `http://127.0.0.1:5000`. No MySQL or AWS setup required to try it —
it runs on SQLite + local file storage by default.

### 3. Config for production (MySQL + S3)

Set these as environment variables (or in a `.env` file):

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

---

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

---

## Design Notes

- **Why abstract storage behind one function (`save_profile_image`)**: the
  routes in `contacts.py` never know or care whether an image ends up on S3
  or local disk. Swapping storage backends later (e.g. moving to Cloudflare
  R2) means touching one file, not every route that handles an upload.
- **Why config-driven DB/storage instead of separate "local" and "prod"
  branches of the app**: environment variables decide behavior at startup,
  so there's exactly one codebase to maintain and test, and moving from a
  laptop to a real deployment is a config change, not a code change.
- **Why per-user contact scoping is enforced at the query level**
  (`Contact.query.filter_by(user_id=current_user.id)`) rather than just in
  the UI: a user directly guessing another contact's URL/ID still can't
  read or modify it — the check lives at the data-access layer, not just
  in what links are shown.

## Possible Next Steps

- Contact tags/categories with filtering
- CSV export
- Pagination for large contact lists
- Unit tests for auth and CRUD routes
