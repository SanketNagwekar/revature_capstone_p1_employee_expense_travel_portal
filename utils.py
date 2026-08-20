from functools import wraps
from flask import session, redirect

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                return redirect("/login")
            if session.get("role") not in roles:
                return redirect("/login")
            return f(*args, **kwargs)
        return decorated
    return decorator
