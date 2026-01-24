from typing import List
from backend_ls.app.config.symbols import LSSYMBOLS, LSSymbolConfig

class LSSymbolProvider:
    """심볼 데이터 소스 추상화"""
    def get_symbols(self) -> List[LSSymbolConfig]:
        raise NotImplementedError
