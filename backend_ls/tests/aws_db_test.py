from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_USER = "hts_admin"
DB_PASS = "hts_admin_pw"     # 🔴 여기 중요
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "hts_real_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine)

def test_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM orders"))
        return result.scalar()

if __name__ == "__main__":
    try:
        count = test_db()
        print("orders count =", count)
    except Exception as e:
        print("DB ERROR:", e)
