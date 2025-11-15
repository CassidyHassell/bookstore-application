from sqlalchemy import create_engine, text, MetaData
from urllib.parse import quote_plus
# Connect to db
import os
import glob
from dotenv import load_dotenv

load_dotenv()  # Loads the .env file

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Password contains a special character, so safety is needed
DB_PASSWORD_SAFE = quote_plus(DB_PASSWORD)

BASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD_SAFE}@{DB_HOST}/"

# Create the database if it doesn't exist
try:
    engine = create_engine(BASE_URI, echo=True)
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`"))
        print(f"Database `{DB_NAME}` ensured.")
except Exception as e:
    print("Error creating the database:", e)

# Now connect to the actual database
try:
    FULL_URI = f"{BASE_URI}{DB_NAME}"
    engine = create_engine(FULL_URI, echo=True)
    print("Connected to the database.")
except Exception as e:
    print("Error connecting to the database:", e)


def run_migration(filepath):
    print(f"Migrating: {filepath}")
    with open(filepath, 'r') as f:
        sql = f.read()

    try:
        with engine.connect() as conn:
            # split each sql statement 
            for statement in sql.strip().split(';'):
                conn.execute(text(statement))
            conn.commit()
    except Exception as e:
        print("Error running migration:", e)
    

# Run all migrations files
def run_all_migrations():
    # grab all migration files ending in .sql
    migrations = sorted(glob.glob(os.path.join("*.sql")))
    print(f"Migration files: {migrations}")
    for migration in migrations:
        run_migration(migration)

# Drop all tables
def drop_all_tables():
    metadata = MetaData()
    print("Dropping tables...")
    try:
        metadata.reflect(bind=engine)
        metadata.drop_all(bind=engine)
        print("All tables dropped")
    except Exception as e:
        print("Error dropping tables from database:", e)

if __name__ == "__main__":
    # Drop all tables, Start from beginning every time for simplicity
    drop_all_tables()
    run_all_migrations()
