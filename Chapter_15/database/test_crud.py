
from database_config import Session
from The_Blueprint import User, Role
from sqlalchemy import select

# This is the full CRUD (Create, Read, Update, Delete) sequence.
# It will run on either SQLite or PostgreSQL based on your 
# J_A_R_V_I_S_ENV environment variable.

print("--- STARTING CRUD TEST ---")

with Session() as session:
    
    # --- 1. CREATE ---
    # We create Python objects and add them to the session.
    
    print("STEP 1: CREATE")
    
    # Create a Role
    admin_role = Role(name="Administrator")
    
    # Create a User and link them to the Role
    # The 'role' attribute uses the relationship() we defined
    tony = User(username="Tony", role=admin_role)
    
    # Add both objects to the "workspace"
    session.add_all([admin_role, tony])
    
    # Commit (save) all changes to the database
    session.commit()
    
    print(f"Created User: {tony.username} with Role: {tony.role.name}")
    print("--- CREATE complete ---")


    # --- 2. READ ---
    # We build a query, execute it, and get our Python object back.
    
#     print("STEP 2: READ")
    
#     # Build the query to find the user named "Tony"
#     stmt = select(User).where(User.username == "Tony")
    
#     # Execute the query. .one() gets exactly one result.
#     found_user = session.execute(stmt).scalars().one()
    
#     print(f"Found User: {found_user.username}, ID: {found_user.id}")
#     print(f"Found User's Role: {found_user.role.name}")
#     print("--- READ complete ---")
    

#     # --- 3. UPDATE ---
#     # We modify the Python object, and the session tracks the change.
    
#     print("STEP 3: UPDATE")
    
#     # We use the 'found_user' object from the previous step
#     found_user.username = "Tony Stark"
    
#     # Commit the change. The session automatically knows this
#     # object was modified and sends the UPDATE command.
#     session.commit()
    
#     print(f"Updated User's name to: {found_user.username}")
#     print("--- UPDATE complete ---")


#     # --- 4. DELETE ---
#     # We tell the session to delete the Python object.
    
#     print("STEP 4: DELETE")
    
#     # We use the same user object
#     session.delete(found_user)
    
#     # Commit the deletion
#     session.commit()
    
#     # Verification: Try to find the user again
#     stmt_verify = select(User).where(User.username == "Tony Stark")
    
#     # .one_or_none() is safer, returning None if not found
#     deleted_user = session.execute(stmt_verify).scalars().one_or_none()
    
#     print(f"Verification find: {deleted_user}")
#     print("--- DELETE complete ---")

# print("--- CRUD TEST FINISHED ---")