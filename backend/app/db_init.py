"""数据库初始化：根据 SQLAlchemy 模型创建表"""

from app.database import Base, engine


def init_tables() -> None:
    Base.metadata.create_all(bind=engine)
