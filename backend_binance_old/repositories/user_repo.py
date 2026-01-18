# backend_binance_old/repositories/user_repo.py
from sqlalchemy.orm import Session
from backend_binance_old.repositories.base_repo import BaseRepository
from backend_binance_old.models.users_model import User


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()


user_repo = UserRepository()
