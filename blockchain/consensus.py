from database import supabase

def is_authorized_validator(user_id: str) -> bool:
    result = (
        supabase.table("authority_nodes")
        .select("node_id")
        .eq("user_id", user_id)
        .eq("status", "ACTIVE")
        .limit(1)
        .execute()
    )
    return bool(result.data)

def require_authorized_validator(user_id: str):
    if not is_authorized_validator(user_id):
        raise PermissionError("User is not an authorized Proof-of-Authority validator.")
