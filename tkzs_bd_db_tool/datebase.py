from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Generator,Type
from .models import Base
import os
import logging
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()
# 获取数据库连接信息
DB_HOST = os.getenv("DB_HOST", None)
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USERNAME", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME_BDDATA", "baidu_source_data")

# 创建数据库连接URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 初始化数据库表
def init_db(base:Type[DeclarativeMeta]|None = None):
    """
    初始化数据库表结构
    :param base: SQLAlchemy 声明基类 (declarative_base)
    """
    if DB_HOST is None:
        logging.error("缺少.env文件，数据库连接信息未配置，请检查环境变量配置")
        raise ValueError("缺少.env文件，数据库连接信息未配置，请检查环境变量配置")
    
    try:
        if base is None:
            base = Base
        base.metadata.create_all(bind=engine)
        logging.info("数据库表初始化成功")
    except Exception as e:
        logging.error(f"数据库表初始化失败: {str(e)}")
        # 根据需要决定是否继续抛出异常
        raise f'数据库表初始化失败: {str(e)}'

# 获取数据库会话
@contextmanager
def get_session()->  Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"数据库会话出错: {str(e)},已经回滚")
    finally:
        session.close()
