import os
from alembic.config import Config
from alembic import command
from dotenv import load_dotenv

load_dotenv()

def run_migrations():
    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5432/coffeedb")
    
    # Ensure we use psycopg (v3) dialect
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    
    # Get the directory where this script lives
    script_dir = os.path.dirname(os.path.abspath(__file__))
    alembic_ini = os.path.join(script_dir, "alembic.ini")
    
    alembic_cfg = Config(alembic_ini)
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    
    print("🚀 Running Alembic migrations...")
    command.upgrade(alembic_cfg, "head")
    print("✅ Migrations applied successfully!")

if __name__ == "__main__":
    run_migrations()
