from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def check_password(hashed: str, password: str) -> bool:
    return check_password_hash(hashed, password)
