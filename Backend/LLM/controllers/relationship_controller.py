from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

from models.user_relationship import UserRelationship


VALID_FIELDS = {"affection", "trust", "comfort"}


class RelationshipController:
    def __init__(self, dsn, base_class):
        self.session_factory = None
        self.dsn = dsn
        self.base_class = base_class

    async def init(self):
        engine = await self._get_engine()
        self.session_factory = await self._get_session(engine)

    async def _get_engine(self):
        engine = create_async_engine(self.dsn, pool_recycle=1200)
        async with engine.begin() as conn:
            await conn.run_sync(self.base_class.metadata.create_all)
        return engine

    @staticmethod
    async def _get_session(engine):
        async_session = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        return async_session

    async def get_relationship(self, user_id: int) -> UserRelationship | None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(UserRelationship).where(
                    UserRelationship.user_id == user_id
                )
            )

            return result.scalar_one_or_none()

    async def reset_relationship(self, user_id: int):
        async with self.session_factory() as session:
            result = await session.execute(
                select(UserRelationship).where(
                    UserRelationship.user_id == user_id
                )
            )

            relationship = result.scalar_one_or_none()

            if relationship is None:
                return False

            relationship.affection = 50
            relationship.trust = 50
            relationship.comfort = 50

            await session.commit()

            return True

    async def modify_relationship(
            self,
            user_id: int,
            changes: dict[str, int]
    ):
        """changes contain json data with "field" and "value" type"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(UserRelationship).where(
                    UserRelationship.user_id == user_id
                )
            )

            relationship = result.scalar_one_or_none()

            if relationship is None:
                relationship = UserRelationship(user_id=user_id)
                session.add(relationship)
                await session.flush()

            for field, amount in changes.items():
                if field not in VALID_FIELDS:
                    raise ValueError(f"Invalid relationship field: {field}")

                current_value = getattr(relationship, field)
                new_value = max(0, min(100, current_value + amount))

                setattr(relationship, field, new_value)

            await session.commit()

            return relationship

