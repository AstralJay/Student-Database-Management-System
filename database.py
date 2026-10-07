from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY

# Auth client: used only for Supabase Auth operations.
auth_client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Server-side database client: service-role key must NEVER be exposed to browsers.
db: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Backwards-compatible name for project modules.
supabase = db
