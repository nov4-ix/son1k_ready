# fix_password_hashes.py
import os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

# Usa tu DB local
os.environ.setdefault("DATABASE_URL", f"sqlite:///{ROOT}/son1k.db")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importa tu modelo y tu hasher real
from backend.app.models import User  # ajusta si tu clase vive en otro módulo
try:
    from backend.app.auth import get_password_hash
except Exception:
    # fallback por si acaso
    from passlib.context import CryptContext
    _pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    def get_password_hash(p): return _pwd.hash(p)

DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

USERS = [
    ("nov4-ix@son1kvers3.com", "admin123", "ADMIN", "ENTERPRISE"),
    ("pro.tester1@son1k.com",  "Premium123!", "PRO", "PRO"),
    ("pro.tester2@son1k.com",  "Premium123!", "PRO", "PRO"),
]

def set_field(u, name, value):
    if hasattr(u, name):
        setattr(u, name, value); return True
    return False

def upsert(email, password, role, plan):
    s = Session()
    try:
        # localiza por email o username
        col = "email" if hasattr(User, "email") else ("username" if hasattr(User, "username") else None)
        if not col: raise RuntimeError("User model no tiene email/username")
        u = s.query(User).filter(getattr(User, col) == email).first()
        if not u:
            u = User()
            set_field(u, col, email)
            set_field(u, "is_active", True)
        # pone hash en el campo correcto
        hp = get_password_hash(password)
        for cand in ("hashed_password", "password_hash", "password"):
            if set_field(u, cand, hp):
                break
        # role/flags/plan si existen
        set_field(u, "role", role)
        if hasattr(u, "is_admin") and role.upper()=="ADMIN":
            u.is_admin = True
        set_field(u, "plan", plan)
        s.add(u); s.commit()
        print(f"✅ {email} actualizado (role={getattr(u,'role',None)} plan={getattr(u,'plan',None)})")
    except Exception as e:
        s.rollback(); raise
    finally:
        s.close()

if __name__ == "__main__":
    for row in USERS: upsert(*row)

