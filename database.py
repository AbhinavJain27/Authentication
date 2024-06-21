from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

url_MYSQL='mysql+pymysql://root:root@localhost:3306/user_verification'
engine=create_engine(url_MYSQL)

SessionLocal=sessionmaker(autoflush=False , autocommit=False , bind=engine)

Base=declarative_base()