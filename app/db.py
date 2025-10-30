import mysql.connector
from mysql.connector import pooling
from .config import settings

connection_pool = pooling.MySQLConnectionPool(
    pool_name="catalog_pool",
    pool_size=5,
    pool_reset_session=True,
    host=settings.MYSQL_HOST,
    database=settings.MYSQL_DB,
    user=settings.MYSQL_USER,
    password=settings.MYSQL_PASSWORD
)

def get_connection():
    return connection_pool.get_connection()
