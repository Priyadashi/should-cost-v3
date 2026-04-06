import json
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, func, TypeDecorator
from app.database import Base


class JSONList(TypeDecorator):
    """Store a Python list as a JSON string (SQLite-compatible)."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    machine_type = Column(String(100), nullable=False)
    hourly_rate = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="INR")
    power_kw = Column(Float, nullable=True)
    commodity_types = Column(JSONList, nullable=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
