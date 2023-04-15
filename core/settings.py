import json
import os
from typing import Any, Final

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
CONFIG = json.loads(open(CONFIG_FILE).read())

# * DATABASE
DB_CONFIG: Final[dict[str, Any]] = CONFIG["DB"]
DB: Final[
    str
] = f"{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset-utf8"
DATABASE_URL: Final[str] = f"mysql+pymysql://{DB}"

# * PASSWORD
PW_HASH_ALGORITHM: Final[str] = "bcrypt"
PW_PATTERN: Final[str] = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,20}$"

# * JWT
JWT_ALGORITHM: Final[str] = "HS256"
JWT_EXPIRE_KEY: Final[str] = "exp"
JWT_SECRET_KEY: Final[str] = CONFIG["SECRET_KEY"]
JWT_SUBJECT_KEY: Final[str] = "sub"
SIGNIN_API_URL: Final[str] = "/users/signin"
TOKEN_EXPIRE_SECONDS: Final[int] = 1800
TOKEN_TYPE: Final[str] = "Bearer"
