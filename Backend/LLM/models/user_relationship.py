from sqlalchemy import Column, Integer, SmallInteger
from sqlalchemy.orm import declarative_base
from sqlalchemy import DateTime
from datetime import datetime

Base = declarative_base()


class UserRelationship(Base):
    __tablename__ = "user_relationship"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    affection = Column(SmallInteger, nullable=False, default=50)
    trust = Column(SmallInteger, nullable=False, default=50)
    comfort = Column(SmallInteger, nullable=False, default=50)

    def __repr__(self):
        return f"affection: {self.affection}, trust: {self.trust}, comfort: {self.comfort}"
