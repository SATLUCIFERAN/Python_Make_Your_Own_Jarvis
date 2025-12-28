

from database_config import Session
from The_Blueprint import User, Role
from sqlalchemy import select
from database_config import engine
print("ENGINE:", engine.url)

# This is the full CRUD (Create, Read, Update, Delete) sequence.
# It will run on either SQLite or PostgreSQL based on your 
# J_A_R_V_I_S_ENV environment variable.

print("--- STARTING CRUD TEST ---")

with Session() as session:
    
        
    print("STEP 1: CREATE")    
    admin_role = Role(name="Administrator")    
    tony = User(username="Tony", role=admin_role)    
    session.add_all([admin_role, tony])    
    session.commit()    
    print(f"Created User: {tony.username} with Role: {tony.role.name}")
    print("--- CREATE complete ---")


    # --- 2. READ ---
    # We build a query, execute it, and get our Python object back.
    
    print("STEP 2: READ")    
    stmt = select(User).where(User.username == "Tony")    
    found_user = session.execute(stmt).scalars().one()    
    print(f"Found User: {found_user.username}, ID: {found_user.id}")
    print(f"Found User's Role: {found_user.role.name}")
    print("--- READ complete ---")
    

    # --- 3. UPDATE ---
    # We modify the Python object, and the session tracks the change.
    
    print("STEP 3: UPDATE")    
    found_user.username = "Tony Stark"    
    session.commit()    
    print(f"Updated User's name to: {found_user.username}")
    print("--- UPDATE complete ---")


    # --- 4. DELETE ---
    # We tell the session to delete the Python object.
    
    print("STEP 4: DELETE")    
    session.delete(found_user)    
    session.commit()    
    stmt_verify = select(User).where(User.username == "Tony Stark")    
    deleted_user = session.execute(stmt_verify).scalars().one_or_none()    
    print(f"Verification find: {deleted_user}")
    print("--- DELETE complete ---")

print("--- CRUD TEST FINISHED ---")