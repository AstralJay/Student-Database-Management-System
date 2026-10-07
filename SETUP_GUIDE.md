# VS Code setup — step by step

## A. Install
1. Python 3.13
2. VS Code
3. Git (optional but recommended)

## B. Open the project
Extract the ZIP and open the extracted folder in VS Code.

## C. Create venv
Open VS Code Terminal:

Windows PowerShell:
```powershell
py -3.13 -m venv venv
venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:
```cmd
venv\Scripts\activate
```

## D. Install packages
```bash
pip install -r requirements.txt
```

## E. Create Supabase project
Create a project at Supabase.

Then:
1. Open SQL Editor.
2. Open `sql/schema.sql`.
3. Paste the entire SQL.
4. Run it.

## F. Get Supabase keys
Dashboard → Project Settings → API.

Copy:
- Project URL → `SUPABASE_URL`
- Publishable/anon key → `SUPABASE_ANON_KEY`
- Service role key → `SUPABASE_SERVICE_ROLE_KEY`

The service-role key is a SECRET. It belongs only in `.env`.

## G. Create `.env`
Copy `.env.example` to `.env` and fill the values.

Example:
```text
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_ANON_KEY=xxxxxxxx
SUPABASE_SERVICE_ROLE_KEY=xxxxxxxx
FLASK_SECRET_KEY=use-a-long-random-value
```

## H. Auth setting for easiest demo
In Supabase:
Authentication → Providers → Email.

For a classroom/demo build, turn off email confirmation so registration immediately works.

For a real deployment, keep email confirmation ON.

## I. Start Flask
```bash
python app.py
```

Then open:
http://127.0.0.1:5000

## J. First demo
### 1. Register faculty
Choose:
- Role: Faculty
- Department: EEE

Faculty registration creates:
- Supabase Auth account
- Faculty profile
- RSA private/public key pair
- Active PoA authority node

### 2. Register student
Choose:
- Role: Student
- Department: EEE

### 3. Login as faculty
Add a course if required.

### 4. Add academic record
Choose:
- student
- course
- semester
- academic year
- marks
- attendance
- grade

When you click Save:
1. Record is stored in Supabase.
2. Transaction is canonicalized.
3. SHA-256 transaction hash is generated.
4. Faculty private key signs the block hash.
5. PoA checks the faculty is an active authority.
6. Block is stored in Supabase.

### 5. Open Blockchain
You can show:
- block number
- previous hash
- transaction hash
- block hash
- validator
- digital signature
- transaction data
- overall VALID/INVALID status

### 6. Edit a record
Editing does not erase blockchain history.
A new `ACADEMIC_RECORD_UPDATED` block is created.

That is an important project demonstration:
**database state changes + immutable blockchain audit history.**

## K. Useful commands
Run tests:
```bash
pytest
```

Check the app:
```bash
python app.py
```

## L. Important project limitation
This is a final-year/minor-project demonstration architecture, not a production university SIS.

For production:
- use proper Supabase RLS and server-side authorization
- use a proper key-management/HSM strategy
- use transactional block creation/locking
- add audit logging and backups
- separate validator nodes rather than keeping all blockchain logic in one Flask process
