from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.engine import Connection
from .settings import get_settings

# The engine is lazy: the first SQL statement opens an actual DB connection.
url = get_settings().database_url
engine_options = {'pool_pre_ping': True}
if url.startswith(('sqlite:', 'sqlite+')):
    # Used exclusively by the self-contained test suite. Production uses PostgreSQL.
    engine_options.update(connect_args={'check_same_thread': False}, poolclass=StaticPool)
else:
    engine_options.update(pool_size=5, max_overflow=5)
engine = create_engine(url, **engine_options)

def get_connection() -> Iterator[Connection]:
    with engine.connect() as conn:
        yield conn
