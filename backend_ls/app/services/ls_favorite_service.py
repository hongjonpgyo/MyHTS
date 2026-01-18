# services/favorite_service.py

from backend_ls.app.repositories.ls_favorite_repo import ls_favorite_repo

class LSFavoriteService:

    def list(self, db, user_id: int):
        return ls_favorite_repo.get_by_user(db, user_id)

    def add(self, db, user_id: int, symbol_code: str):
        if ls_favorite_repo.get_one(db, user_id, symbol_code):
            return None
        return ls_favorite_repo.create(db, user_id, symbol_code)

    def remove(self, db, user_id: int, symbol_code: str):
        return ls_favorite_repo.delete(db, user_id, symbol_code)

ls_favorite_service = LSFavoriteService()