from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

from .settings import DATABASE_URL

# * pool_recycle=500 연결을 재활용하고 새 연결로 교체해야 하는 시간(500초)
# * 오래된 연결 혹은 연결이 끊기는 것을 방지하기 위한 것
# * 새 연결이 요청될 때 연결이 500초 이상 열려 있는지 확인
# * 연결이 지정된 시간보다 오랫동안 열려 있으면 닫히고 새 연결로 대체
# * 이는 세션 연결이 끊어지고 새 연결을 사용하여 새 세션이 생성됨을 의미
# * echo=True로 지정할 시 shell에 sql query logging
DB_ENGINE = create_engine(DATABASE_URL, pool_recycle=500, echo=False)


# * Session: Application이 DB에 연결되어 작업을 수행하는 기간
# * transaction 실행 및 여러 작업을 수행.
def get_session() -> Iterator[Session]:
    """DB Session 반환"""
    with Session(DB_ENGINE) as session:
        yield session


def conn() -> None:
    """DB 연결 및 App 실행 시 새롭게 정의된 모델 table 자동 생성"""
    SQLModel.metadata.create_all(DB_ENGINE)
