from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import create_engine, Column, Integer, String, Boolean, or_
from termcolor import colored


''' Engine '''

DB_ENGINE = "sqlite"
DB_API = "pysqlite"
DB_PATH = "LÑdb.db"
ENGINE = create_engine(f"{DB_ENGINE}+{DB_API}:///{DB_PATH}", echo=True, future=True)


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


''' Schema generation '''

Base.metadata.create_all(ENGINE)


''' Functions '''

def get_news_links():
    '''
    News links set.
        SELECT n.link FROM new n
        GROUP BY n.link
        ORDER BY n.code DESC
    '''
    query_result_list = list()
    with Session(ENGINE) as session:
        query_result = session.query(New.link).group_by(New.link).order_by(New.code.desc())
        for element in query_result:
            query_result_list.append(element[0])
    return query_result_list


def insert_new_link(new_link, new_source):
    '''
    Insert new link.
        INSERT INTO new (link, source)
        VALUES (new_link, new_source)
    '''
    with Session(ENGINE) as session:
        new = New(link=new_link, source=new_source)
        session.add_all([new])
        session.commit()


def get_no_code_links():
    query_result_set = set()
    session = Session(ENGINE)
    query_result = session.query(New.link).filter(or_(New.code == None, New.code == ""),
                                                  New.valid == None,
                                                  New.excluded == None).order_by(New.link)
    for element in query_result:
        query_result_set.add(element[0])
    return query_result_set


def update_new_code(new_link, new_code):
    '''
    Update new code.
        UPDATE new
        SET code = new_code
        WHERE link = new_code
    '''
    with Session(ENGINE) as session:
        new = session.query(New).filter(New.link == new_link).first()
        new.code = new_code
        session.commit()


def get_no_date_links():
    query_result_set = set()
    session = Session(ENGINE)
    query_result = session.query(New.link).filter(New.year == None)
    for element in query_result:
        query_result_set.add(element[0])
    return query_result_set


def update_new_date(new_link, new_date):
    with Session(ENGINE) as session:
        new = session.query(New).filter(New.link == new_link).first()
        new.day = new_date.day
        new.month = new_date.month
        new.year = new_date.year
        session.commit()


def update_new_valid(new_link, valid):
    with Session(ENGINE) as session:
        new = session.query(New).filter(New.link == new_link).first()
        new.valid = valid
        session.commit()


def update_new_excluded(new_link, excluded):
    with Session(ENGINE) as session:
        new = session.query(New).filter(New.link == new_link).first()
        new.excluded = excluded
        session.commit()