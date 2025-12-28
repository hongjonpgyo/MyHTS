# backend/services/auth_service.py
import bcrypt
# import jwt
import secrets
import hashlib

from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta

from backend.repositories.user_repo import user_repo
from backend.repositories.account_repo import account_repo
from backend.config.settings import SECRET_KEY, ALGORITHM

class AuthService:
    # SECRET_KEY = "CHANGE_ME_SECRET"   # TODO: 환경변수/설정에서 가져오도록 변경 권장
    # ALGORITHM = "HS256"

    def login(self, db: Session, email: str, password: str):
        # 1) 사용자 조회
        user = user_repo.get_by_email(db, email)
        if not user:
            # FastAPI가 JSON으로 내려줄 수 있도록 HTTPException 사용
            raise HTTPException(status_code=400, detail="Invalid email or password")

        # 2) 비밀번호 체크 (users.password_hash 기준)
        # users 테이블: password_hash 컬럼 사용 중 (bcrypt 해시)
        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            raise HTTPException(status_code=400, detail="Invalid email or password")

        # 3) JWT 발급
        payload = {
            "user_id": user.user_id,
            "email": user.email,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        # 4) 기본 계좌 조회 (없으면 에러)
        account = account_repo.get_primary_account(db, user.user_id)
        if not account:
            raise HTTPException(status_code=400, detail="No account for this user")

        # 5) auth_api에서 언급된 형태로 반환
        return user, token, account.account_id

    @staticmethod
    def get_user_id_from_token(token: str) -> int | None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return int(payload.get("user_id"))
        except JWTError:
            return None

    @staticmethod
    def request_password_reset(self, db, email: str):
        user = user_repo.get_by_email(db, email)
        if not user:
            # 보안상 존재 여부 숨김
            return

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        user.reset_token_hash = token_hash
        user.reset_token_expire = datetime.utcnow() + timedelta(minutes=30)

        db.commit()

        # 🔥 지금은 콘솔 출력 (나중에 메일로 교체)
        print("🔐 PASSWORD RESET TOKEN")
        print(f"email: {email}")
        print(f"token: {raw_token}")

    @staticmethod
    def reset_password(self, db, raw_token: str, new_password: str):
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        user = user_repo.get_by_reset_token(db, token_hash)
        if not user:
            raise Exception("유효하지 않은 토큰")

        if user.reset_token_expire < datetime.utcnow():
            raise Exception("토큰이 만료되었습니다")

        user.password_hash = bcrypt.hash(new_password)
        user.reset_token_hash = None
        user.reset_token_expire = None

        db.commit()

auth_service = AuthService()
