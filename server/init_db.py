from app import app, db
import pymysql

# Install pymysql as mysqldb if not already done (optional, but good for some sqlalchemy versions)
pymysql.install_as_MySQLdb()

def init_db():
    print("Attempting to connect to MySQL database...")
    try:
        with app.app_context():
            print("Creating tables...")
            db.create_all()
            print("Tables created successfully!")
            
            # Optional: Verify tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables in database: {tables}")
            
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
