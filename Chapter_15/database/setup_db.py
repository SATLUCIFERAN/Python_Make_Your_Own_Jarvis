# 1. Bring in the Models (The Blueprints/Base)
# IMPORTANT: We must explicitly import the model classes (User, Role) 
# so the ORM can register them with Base's metadata (the master plan).
from The_Blueprint import Base, User, Role 

# 2. Bring in the Engine (The Contractor/engine)
from database_config import engine 

# 3. Issue the Build Order! (Base.metadata is the master plan)
print("Starting database construction...")
Base.metadata.create_all(engine)
print("Database tables created successfully!")
print(engine.url)