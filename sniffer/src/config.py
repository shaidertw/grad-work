from os import environ
from dotenv import load_dotenv

load_dotenv(".env")

#from loguru import logger
#
#logger.add("api.log", format="{time} {level} {message}", level="DEBUG", retention="2 days")

CONNECTION_STRING = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
    environ["DB_LOGIN"],
    environ["DB_PASSWORD"],
    environ["DB_HOST"],
    environ["DB_PORT"],
    environ["DB_NAME"]
)
