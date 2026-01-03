# services/favorite_service.py
class FavoriteService:
    def __init__(self, repo):
        self.repo = repo

    def list(self, db, user_id: int):
        return self.repo.get_by_user(db, user_id)

    def add(self, db, user_id: int, symbol_code: str):
        if self.repo.get_one(db, user_id, symbol_code):
            return None
        return self.repo.create(db, user_id, symbol_code)

    def remove(self, db, user_id: int, symbol_code: str):
        return self.repo.delete(db, user_id, symbol_code)
