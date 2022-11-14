from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import create_engine, Column, Integer, String, Boolean, or_


''' Engine '''

DB_ENGINE = "sqlite"
DB_API = "pysqlite"
DB_PATH = "LÑdb.db"
ENGINE = create_engine(f"{DB_ENGINE}+{DB_API}:///{DB_PATH}", echo=True, future=True)
STATUS_CODES_ERROR = [404, 500]


''' ClassTables '''

Base = declarative_base()

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, nullable=False)
    link = Column(String, nullable=False)
    source = Column(String, nullable=False)
    code = Column(Integer, nullable=False)
    title = Column(String, nullable=True)
    author = Column(String, nullable=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
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
        ORDER BY n.code ASC
    '''
    query_result_list = list()
    with Session(ENGINE) as session:
        query_result = session.query(News.link).order_by(News.code.asc())
        for element in query_result:
            query_result_list.append(element[0])
    return query_result_list


def get_unvalid_links():
    '''
    News links set.
        SELECT n.link FROM new n
        GROUP BY n.link
        ORDER BY n.code ASC
    '''
    query_result_list = list()
    with Session(ENGINE) as session:
        query_result = session.query(News.link).filter(or_(News.valid == False,
                                                          News.valid == None)).group_by(News.link).order_by(News.code.asc())
        for element in query_result:
            query_result_list.append(element[0])
    return query_result_list


def insert_new_link(new_link, new_source, new_code, new_title, new_author, new_year, new_month, new_day):
    '''
    Insert new link.
        INSERT INTO new (link, source, code, title, author, year, month, day)
        VALUES (new_link, new_source, new_code, new_title, new_author new_year, new_month, new_day)
    '''
    with Session(ENGINE) as session:
        new = News(link=new_link,
                   source=new_source,
                   code=new_code,
                   title=new_title,
                   author=new_author,
                   year=new_year,
                   month=new_month,
                   day=new_day
        )
        session.add_all([new])
        session.commit()


def get_no_code_links():
    query_result_set = set()
    session = Session(ENGINE)
    query_result = session.query(News.link).filter(News.code == None)
    # query_result = session.query(News.link).filter(or_(News.code == None, News.code == ""),
    #                                               News.valid == None,
    #                                               News.excluded == None).order_by(News.link)
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
        new = session.query(News).filter(News.link == new_link).first()
        News.code = new_code
        session.commit()


def get_no_date_links():
    query_result_set = set()
    session = Session(ENGINE)
    query_result = session.query(News.link).filter(or_(News.year == None,
                                                      News.month == None,
                                                      News.day == None))
    for element in query_result:
        query_result_set.add(element[0])
    return query_result_set


def update_new_link(old_link, new_link):
    with Session(ENGINE) as session:
        new = session.query(News).filter(News.link == old_link).first()
        News.link = new_link
        session.commit()


def update_new_date(new_link, new_date):
    with Session(ENGINE) as session:
        new = session.query(News).filter(News.link == new_link).first()
        News.day = new_date.day
        News.month = new_date.month
        News.year = new_date.year
        session.commit()


def update_new_valid(new_link, valid):
    with Session(ENGINE) as session:
        new = session.query(News).filter(News.link == new_link).first()
        News.valid = valid
        session.commit()


def update_new_excluded(new_link, excluded):
    with Session(ENGINE) as session:
        new = session.query(News).filter(News.link == new_link).first()
        News.excluded = excluded
        session.commit()


def delete_new(new_link):
  with Session(ENGINE) as session:
    new = session.query(News).filter(News.link == new_link).first()
    session.delete(new)
    session.commit()


''' Titles & Authors '''

def get_no_title_no_author_links():
    query_result_list = list()
    with Session(ENGINE) as session:
        query_result = session.query(News.link).filter(News.title == None, News.author == None).order_by(News.code.asc())
        for element in query_result:
            query_result_list.append(element[0])
    return query_result_list


def update_title(link, title):
  with Session(ENGINE) as session:
    news = session.query(News).filter(News.link == link).first()
    news.title = title
    session.commit()


def update_author(link, author):
  with Session(ENGINE) as session:
    news = session.query(News).filter(News.link == link).first()
    news.author = author
    session.commit()


''' Data original '''

def get_no_data_original_links():
    query_result_list = list()
    with Session(ENGINE) as session:
        query_result = session.query(News.link).filter(News.data_original == None).order_by(News.code.asc())
        for element in query_result:
            query_result_list.append(element[0])
    return query_result_list


def update_data_orginal(link, data_original):
  with Session(ENGINE) as session:
    news = session.query(News).filter(News.link == link).first()
    news.data_original = data_original
    session.commit()


''' Data arranged '''

def get_no_data_arranged_links():
    query_result_list = list()
    with Session(ENGINE) as session:
        query_result = session.query(News.link).filter(News.data_arranged == None).order_by(News.code.asc())
        for element in query_result:
            query_result_list.append(element[0])
    return query_result_list


def get_data_original(news_link):
    with Session(ENGINE) as session:
        data_original = session.query(News.data_original).filter(News.link == news_link).first()
    return data_original[0]


def update_data_arranged(link, data_arranged):
    with Session(ENGINE) as session:
        news = session.query(News).filter(News.link == link).first()
        news.data_original = data_arranged
        session.commit()