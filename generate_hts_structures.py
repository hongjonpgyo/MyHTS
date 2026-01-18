import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------
# Utility
# -------------------------------------------------
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"[CREATE] Folder created: {path}")

def write_file(path, content, overwrite=False):
    if os.path.exists(path) and not overwrite:
        print(f"[SKIP] File exists: {path}")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[WRITE] File written: {path}")

def ensure_init(path):
    init_file = os.path.join(path, "__init__.py")
    write_file(init_file, "", overwrite=False)


# -------------------------------------------------
# Base Repository
# -------------------------------------------------
BASE_REPO_CONTENT = """
from sqlalchemy.orm import Session

class BaseRepository:
    model = None

    def get(self, db: Session, id: int):
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session):
        return db.query(self.model).all()

    def create(self, db: Session, **kwargs):
        obj = self.model(**kwargs)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, obj):
        db.delete(obj)
        db.commit()
"""

# -------------------------------------------------
# Repository Templates
# -------------------------------------------------

REPOSITORY_TEMPLATES = {
    "account_repo.py": """
from backend_binance_old.repositories.base_repo import BaseRepository
from backend_binance_old.models.account_model import Account

class AccountRepository(BaseRepository):
    model = Account
""",
    "position_repo.py": """
from backend_binance_old.repositories.base_repo import BaseRepository
from backend_binance_old.models.position_model import Position

class PositionRepository(BaseRepository):
    model = Position

    def get_by_account(self, db, account_id: int):
        return db.query(self.model).filter(self.model.account_id == account_id).all()
""",
    "order_repo.py": """
from backend_binance_old.repositories.base_repo import BaseRepository
from backend_binance_old.models.order_model import Order

class OrderRepository(BaseRepository):
    model = Order
""",
    "execution_repo.py": """
from backend_binance_old.repositories.base_repo import BaseRepository
from backend_binance_old.models.execution_model import Execution

class ExecutionRepository(BaseRepository):
    model = Execution
""",
    "symbol_repo.py": """
from backend_binance_old.repositories.base_repo import BaseRepository
from backend_binance_old.models.symbol_model import Symbol

class SymbolRepository(BaseRepository):
    model = Symbol

    def get_by_code(self, db, code: str):
        return db.query(self.model).filter(self.model.code == code).first()
"""
}

# -------------------------------------------------
# Model Templates
# -------------------------------------------------
MODEL_TEMPLATES = {
    "ls_futures_account_model.py": """
from sqlalchemy import Column, Integer, Float, String
from backend_binance_old.db.database import Base

class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    margin = Column(Float, default=0.0)
    pnl = Column(Float, default=0.0)
""",
    "position_model.py": """
from sqlalchemy import Column, Integer, Float
from backend_binance_old.db.database import Base

class Position(Base):
    __tablename__ = "positions"

    position_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, index=True)
    symbol_id = Column(Integer, index=True)
    qty = Column(Float, default=0.0)
    avg_price = Column(Float, default=0.0)
""",
    "order_model.py": """
from sqlalchemy import Column, Integer, Float, String
from backend_binance_old.db.database import Base

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer)
    symbol_id = Column(Integer)
    side = Column(String)
    qty = Column(Float)
    exec_price = Column(Float, nullable=True)
""",
    "execution_model.py": """
from sqlalchemy import Column, Integer, Float, String
from backend_binance_old.db.database import Base

class Execution(Base):
    __tablename__ = "executions"

    exec_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer)
    account_id = Column(Integer)
    symbol_id = Column(Integer)
    side = Column(String)
    qty = Column(Float)
    price = Column(Float)
""",
    "symbol_model.py": """
from sqlalchemy import Column, Integer, String
from backend_binance_old.db.database import Base

class Symbol(Base):
    __tablename__ = "symbols"

    symbol_id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)
    name = Column(String)
"""
}

# -------------------------------------------------
# Schema Templates
# -------------------------------------------------
SCHEMA_TEMPLATES = {
    "ls_account_schema.py": """
from pydantic import BaseModel

class AccountSchema(BaseModel):
    account_id: int
    balance: float
    margin: float
    pnl: float

    class Config:
        orm_mode = True
""",
    "ls_position_schema.py": """
from pydantic import BaseModel

class PositionSchema(BaseModel):
    position_id: int
    account_id: int
    symbol_id: int
    qty: float
    avg_price: float

    class Config:
        orm_mode = True
""",
    "ls_order_schema.py": """
from pydantic import BaseModel

class OrderCreate(BaseModel):
    account_id: int
    symbol: str
    side: str
    qty: float
""",
    "execution_schema.py": """
from pydantic import BaseModel

class ExecutionSchema(BaseModel):
    exec_id: int
    order_id: int
    account_id: int
    symbol_id: int
    side: str
    qty: float
    price: float

    class Config:
        orm_mode = True
""",
    "symbol_schema.py": """
from pydantic import BaseModel

class SymbolSchema(BaseModel):
    symbol_id: int
    code: str
    name: str

    class Config:
        orm_mode = True
"""
}

# -------------------------------------------------
# Directory generation
# -------------------------------------------------
def generate():
    print("\n===== HTS 구조 자동 생성 시작 =====")

    repo_dir = os.path.join(BASE_DIR, "backend_binance_old", "repositories")
    model_dir = os.path.join(BASE_DIR, "backend_binance_old", "models")
    schema_dir = os.path.join(BASE_DIR, "backend_binance_old", "schemas")

    for d in [repo_dir, model_dir, schema_dir]:
        ensure_dir(d)
        ensure_init(d)

    # Base repo
    write_file(os.path.join(repo_dir, "base_repo.py"), BASE_REPO_CONTENT)

    # Repositories
    for filename, content in REPOSITORY_TEMPLATES.items():
        write_file(os.path.join(repo_dir, filename), content)

    # Models
    for filename, content in MODEL_TEMPLATES.items():
        write_file(os.path.join(model_dir, filename), content)

    # Schemas
    for filename, content in SCHEMA_TEMPLATES.items():
        write_file(os.path.join(schema_dir, filename), content)

    print("===== 완료! HTS Repository / Model / Schema 자동 생성됨 =====\n")


if __name__ == "__main__":
    generate()
