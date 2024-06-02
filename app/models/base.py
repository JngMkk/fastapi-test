from datetime import date, datetime
from typing import Any, Sequence, TypeVar

from sqlalchemy import TIMESTAMP, Date, Integer, delete, desc, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.exceptions import ConflictException, NotFoundException, ServiceUnavailableException

ModelType = TypeVar("ModelType", bound="ModelBase")


class ModelBase(DeclarativeBase):
    """Base Model"""

    type_annotation_map = {int: Integer, datetime: TIMESTAMP, date: Date}

    id: Any
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), doc="Time of Creation.")
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), doc="Time of last Modification."
    )

    @classmethod
    async def get(
        cls: type[ModelType], db: AsyncSession, conditions: Sequence[Any] | None = None
    ) -> ModelType:
        """조건에 맞는 첫 번째 레코드 반환

        Args:
            cls (type[_MBT]): BaseModel 상속받은 모델
            db (AsyncSession): db session
            conditions (Sequence[Any]): where절에 들어갈 조건

        Returns:
            _MBT: BaseModel 상속받은 model 인스턴스 반환 (레코드) or None
        """

        if conditions is None:
            conditions = []

        stmt = select(cls).where(*conditions)
        result = await db.execute(stmt)
        record = result.scalars().first()
        if record is None:
            raise NotFoundException
        return record

    @classmethod
    async def list(
        cls: type[ModelType],
        db: AsyncSession,
        conditions: Sequence[Any] | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Sequence[ModelType]:
        if conditions is None:
            conditions = []

        stmt = select(cls).where(*conditions).offset(offset).limit(limit).order_by(desc(cls.id))
        result = await db.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def delete(cls: type[ModelType], db: AsyncSession, conditions: Sequence[Any]) -> None:
        """조건에 맞는 레코드 삭제

        Args:
            cls (type[_MBT]): BaseModel 상속받은 모델
            db (AsyncSession): db session
            conditions (Sequence[Any]): where절에 들어갈 조건
        """
        stmt = delete(cls).where(*conditions)
        try:
            await db.execute(stmt)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise ServiceUnavailableException
        return

    @classmethod
    async def update(
        cls: type[ModelType], db: AsyncSession, instance: ModelType, **kwargs: Any
    ) -> ModelType:
        """
        Args:
            cls (type[_MBT]): BaseModel 상속받은 모델
            db (AsyncSession): db session
            instance (_MBT): 모델 인스턴스

        Returns:
            _MBT: 업데이트된 instance 반환
        """
        for k, v in kwargs.items():
            setattr(instance, k, v)

        try:
            await db.commit()
            await db.refresh(instance)
        except SQLAlchemyError as e:
            await db.rollback()
            if isinstance(e, IntegrityError):
                raise ConflictException
            raise ServiceUnavailableException
        return instance

    @classmethod
    async def create(cls: type[ModelType], db: AsyncSession, instance: ModelType) -> ModelType:
        """
        Args:
            cls (type[_MBT]): BaseModel 상속받은 모델
            db (AsyncSession): db session
            instance (_MBT): 모델 instance

        Returns:
            _MBT: 정상적으로 추가된 레코드 반환
        """

        db.add(instance)
        try:
            await db.commit()
            await db.refresh(instance)
        except SQLAlchemyError as e:
            await db.rollback()
            if isinstance(e, IntegrityError):
                raise ConflictException
            raise ServiceUnavailableException
        return instance
