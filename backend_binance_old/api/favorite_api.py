# api/routes/favorite.py
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from backend_binance_old.schemas.favorite import FavoriteCreate, FavoriteOut
from backend_binance_old.repositories.favorite_repo import FavoriteRepository
from backend_binance_old.services.auth_service import AuthService
from backend_binance_old.services.favorite_service import FavoriteService
from backend_binance_old.db.database import get_db

router = APIRouter(prefix="/favorites", tags=["Favorites"])

repo = FavoriteRepository()
service = FavoriteService(repo)


@router.get("", response_model=list[FavoriteOut])
def get_favorites(
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    token = authorization.replace("Bearer ", "")
    user_id = AuthService.get_user_id_from_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    return service.list(db, user_id)



@router.post("", response_model=FavoriteOut)
def add_favorite(
    data: FavoriteCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    token = authorization.replace("Bearer ", "")
    user_id = AuthService.get_user_id_from_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    fav = service.add(db, user_id, data.symbol_code)
    if not fav:
        raise HTTPException(status_code=409, detail="Already exists")

    return fav



@router.delete("/{symbol_code}")
def delete_favorite(
    symbol_code: str,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    token = authorization.replace("Bearer ", "")
    user_id = AuthService.get_user_id_from_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    ok = service.remove(db, user_id, symbol_code)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")

    return {"ok": True}

