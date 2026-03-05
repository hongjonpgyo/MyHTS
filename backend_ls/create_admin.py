from backend_ls.app.db.ls_db import SessionLocal
from backend_ls.app.models.admin_user_model import AdminUser
from backend_ls.app.core.security import hash_password

db = SessionLocal()

username = "admin"
password = "admin1234"

admin = AdminUser(
    username=username,
    password_hash=hash_password(password),
    role="superadmin"
)

db.add(admin)
db.commit()

print("Admin created.")