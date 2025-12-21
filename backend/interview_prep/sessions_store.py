import uuid
import time
import json
import os
import redis

# --- Redis Configuration ---
# Use the REDIS_URL from environment variable, default to localhost:6379
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/1") # Using DB 1 for session metadata
REDIS_SESSION_PREFIX = "session:metadata:"

redis_client = redis.from_url(REDIS_URL)

def create_session(title="New Chat"):
    session_id = str(uuid.uuid4())
    session_meta = {
        "session_id": session_id,
        "title": title,
        "created_at": int(time.time()),
    }
    redis_client.set(REDIS_SESSION_PREFIX + session_id, json.dumps(session_meta))
    return session_meta


def list_sessions():
    session_keys = redis_client.keys(REDIS_SESSION_PREFIX + "*")
    sessions = []
    for key in session_keys:
        data = redis_client.get(key)
        if data:
            sessions.append(json.loads(data))
    
    # Return newest first
    return sorted(sessions, key=lambda x: x["created_at"], reverse=True)


def delete_session(session_id):
    # Delete session metadata from Redis
    result = redis_client.delete(REDIS_SESSION_PREFIX + session_id)
    return result > 0 # Return True if at least one key was deleted

def get_session(session_id: str):
    """
    Retrieves a single session's metadata from Redis.
    """
    key = REDIS_SESSION_PREFIX + session_id
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None


def update_session_title(session_id: str, new_title: str):
    key = REDIS_SESSION_PREFIX + session_id
    data = redis_client.get(key)
    if data:
        session_meta = json.loads(data)
        session_meta["title"] = new_title
        redis_client.set(key, json.dumps(session_meta))
        return True
    return False