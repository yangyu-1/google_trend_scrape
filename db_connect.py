from sqlalchemy import create_engine
import os
from sqlalchemy.pool import NullPool


def mysql_conn():
    try:
        db_user = os.environ["db_user"]
        db_pass = os.environ["db_pass"]
        db_uri = os.environ["db_uri"]
        connection_trying = (
            f"mysql+pymysql://{db_user}:{db_pass}@{db_uri}:3306/amazon_scrape"
        )
        engine = create_engine(
            connection_trying, poolclass=NullPool, pool_pre_ping=True
        )
    except KeyError:
        raise Exception('''Please set db_user, db_pass and db_uri"''')
    return engine


# NOTES:
# Second Measure can provide Retail and social media spend.
# Do they have API Access?
