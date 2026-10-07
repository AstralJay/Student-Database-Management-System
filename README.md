# Blockchain-Based Academic Database Management System

A Flask + Supabase + custom Proof-of-Authority blockchain academic database.

## Main features
- Student and faculty authentication through Supabase Auth
- Academic course database
- Student marks, attendance, semester and grade records
- Faculty creates and updates academic records
- Every create/update operation is hashed with SHA-256
- Faculty validators use RSA digital signatures
- Proof-of-Authority checks authorized faculty validators
- Blockchain blocks are stored in Supabase PostgreSQL
- Blockchain integrity verification
- Student dashboard and faculty dashboard

## 1. Create the project
Open this folder in VS Code.

## 2. Create virtual environment

Windows:
    py -3.13 -m venv venv
    venv\Scripts\activate

macOS/Linux:
    python3 -m venv venv
    source venv/bin/activate

## 3. Install packages
    pip install -r requirements.txt

## 4. Configure Supabase
Create a Supabase project.

Open SQL Editor and run:
    sql/schema.sql

Copy `.env.example` to `.env` and fill:
    SUPABASE_URL=...
    SUPABASE_ANON_KEY=...
    SUPABASE_SERVICE_ROLE_KEY=...
    FLASK_SECRET_KEY=...

Use both:
- SUPABASE_ANON_KEY: used for Supabase Auth.
- SUPABASE_SERVICE_ROLE_KEY: used only by the Flask server for database operations.

NEVER put SUPABASE_SERVICE_ROLE_KEY in HTML, JavaScript, GitHub, or any client-side code.

## 5. Authentication
For a simple college demonstration:
Supabase Dashboard -> Authentication -> Providers -> Email.
You can turn off email confirmation if you want immediate registration.

## 6. Run
    python app.py

Open:
    http://127.0.0.1:5000

## 7. Demo flow
1. Register a faculty account.
2. Register a student account.
3. Log in as faculty.
4. Add a course if needed.
5. Add an academic record.
6. The faculty record is signed and added to the blockchain.
7. Log in as the student to view the record.
8. Open Blockchain to show the blocks and verification status.
9. Edit the record as faculty.
10. A new blockchain block is created for the update.

## Security notes
- Never commit `.env`.
- Never commit private RSA keys.
- Private validator keys are stored under `keys/<user_id>/private_key.pem`.
- This is an academic/demo blockchain, not a production university information system.
