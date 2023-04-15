from fastapi import Depends

from core.auth import authenticate
from core.database import get_session

# ! 의존성 주입
SESSION = Depends(get_session)  # * DB Session 의존성 주입
CURR_USER = Depends(authenticate)  # * 현재 Session User auth validation 의존성 주입
