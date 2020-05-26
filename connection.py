import logging
import psycopg2 as pg

logger = logging.getLogger(__name__)

connection = pg.connect(
    "host=localhost port=5432 user=postgres password=1234qwer dbname=linkshorter"
)
logger.debug("New database connection!")
