from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class LoginSession:
    token: str
    created_at: float
    last_seen_at: float


class SessionManager:
    """
    account_id 기준 세션/스트림 관리.
    - login: account_id -> LoginSession
    - stream: account_id -> asyncio.Queue (SSE 종료 시그널용)
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._login: Dict[str, LoginSession] = {}
        self._stream: Dict[str, asyncio.Queue] = {}

    # -----------------------------
    # Login session
    # -----------------------------
    def is_active(self, account_id: str) -> bool:
        with self._lock:
            return account_id in self._login

    def register_login(self, account_id: str, token: str) -> bool:
        """
        로그인 등록.
        return: 기존 세션이 있었는지 (already_logged_in)
        """
        now = time.time()
        with self._lock:
            already = account_id in self._login
            self._login[account_id] = LoginSession(
                token=token,
                created_at=now,
                last_seen_at=now,
            )
            return already

    def touch(self, account_id: str) -> None:
        with self._lock:
            s = self._login.get(account_id)
            if s:
                s.last_seen_at = time.time()

    def logout(self, account_id: str) -> None:
        with self._lock:
            self._login.pop(account_id, None)
        # 스트림도 끊기
        self.disconnect_stream(account_id)

    # -----------------------------
    # SSE stream (one per account)
    # -----------------------------
    def register_stream(self, account_id: str, q: asyncio.Queue) -> None:
        """
        SSE 연결 등록. 기존 스트림이 있으면 끊는다.
        """
        # 기존 스트림 끊고 새로 등록
        self.disconnect_stream(account_id)
        with self._lock:
            self._stream[account_id] = q

    def disconnect_stream(self, account_id: str) -> None:
        """
        등록된 SSE 큐에 종료 시그널(None) 넣어서 generator 종료 유도
        """
        with self._lock:
            q = self._stream.pop(account_id, None)
        if q:
            try:
                q.put_nowait(None)
            except Exception:
                pass


# ✅ 모듈 전역 인스턴스 = (단일 프로세스 기준) 싱글톤
session_manager = SessionManager()
