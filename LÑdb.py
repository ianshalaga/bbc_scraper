from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Boolean


def get_db_engine():
    db_engine = "sqlite"
    db_api = "pysqlite"
    db_path = "LÑdb.db"
    engine = create_engine(f"{db_engine}+{db_api}:///{db_path}", echo=True, future=True)
    return engine


''' ClassTables '''

Base = declarative_base()

class New(Base):
    __tablename__ = "new"

    id = Column(Integer, primary_key=True, nullable=False)
    link = Column(String, nullable=False)
    source = Column(String, nullable=False)
    code = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    month = Column(Integer, nullable=True)
    day = Column(Integer, nullable=True)
    valid = Column(Boolean, nullable=True)
    excluded = Column(Boolean, nullable=True)
    video = Column(Boolean, nullable=True)
    uploaded = Column(Boolean, nullable=True)
    data_original = Column(String, nullable=True)
    data_arranged = Column(String, nullable=True)


''' Engine '''

engine = get_db_engine()


''' Schema generation '''

Base.metadata.create_all(engine)