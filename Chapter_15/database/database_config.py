
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# 1. Read the Environment: Get the setting from the operating system
# Uses 'development' as a safe default if J_A_R_V_I_S_ENV is not set.
ENV = os.environ.get("J_A_R_V_I_S_ENV", "development") 

# 2. Determine the Site & Build the String
if ENV == "production":
    # 2a. PostgreSQL Connection: Securely pulls credentials from environment
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASS"] 
    host = os.environ["DB_HOST"]
    
    # Credentials are URL-encoded (quote_plus) for security and stability
    DB_URL = f"postgresql://{quote_plus(user)}:{quote_plus(password)}@{host}/prod_db"
    connect_args = {}
else:
    # 2b. SQLite Connection: Local file path
    DB_URL = "sqlite:///./local_cache.db"
    # check_same_thread=False is needed for multi-threaded access in development
    connect_args = {"check_same_thread": False}

# 3. Hire the Contractor: Create the Engine (The primary connection tool)
# future=True enables modern SQLAlchemy 2.0 style operation.
engine = create_engine(DB_URL, connect_args=connect_args, future=True) 

# 3a. Enable SQLite Foreign Keys (Critical Fix!)
# SQLite requires PRAGMA foreign_keys=ON to be run upon every connection.
if DB_URL.startswith("sqlite"):    
    # The event hook ensures this command runs every time a new connection is made.
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# 4. Prepare the Session Factory
# The factory creates the session objects used for querying and transactions.
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
