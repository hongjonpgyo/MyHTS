from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend_binance_old.services.auth_service import auth_service
from backend_binance_old.db.database import get_db
from backend_binance_old.utils.password import hash_password
from backend_binance_old.repositories.user_repo import UserRepository

router = APIRouter(prefix="/auth", tags=["Auth"])

user_repo = UserRepository()

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    account_id: int

class SignupRequest(BaseModel):
    email: str
    password: str

class FindIdRequest(BaseModel):
    email: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 🔹 JSON body 로 들어온 값 사용
    user, token, account_id = auth_service.login(
        db, payload.email, payload.password
    )

    return LoginResponse(
        access_token=token,
        user_id=user.user_id,
        account_id=account_id,
    )

@router.post("/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    if len(req.password) < 6:
        raise HTTPException(400, "비밀번호는 6자 이상")

    if user_repo.get_by_email(db, req.email):
        raise HTTPException(400, "이미 존재하는 이메일")

    password_hash = hash_password(req.password)

    user_repo.create(
        db=db,
        email=req.email,
        password_hash=password_hash,
    )

    return {"ok": True}

@router.post("/find-id")
def find_id(payload: FindIdRequest, db: Session = Depends(get_db)):
    print(payload.email)
    user = user_repo.get_by_email(db, payload.email)
    if not user:
        raise HTTPException(404, "User not found")

    return {"email": user.email}

@router.post("/password/reset/request")
def request_password_reset(
    payload: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    auth_service.request_password_reset(db, payload.email)
    return {"ok": True}

@router.post("/password/reset/confirm")
def reset_confirm(
    payload: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    auth_service.reset_password(
        db, payload.token, payload.new_password
    )
    return {"ok": True}
