 
    print("STEP 4: DELETE")    
    session.delete(found_user)    
    session.commit()    
    stmt_verify = select(User).where(User.username == "Tony Stark")    
    deleted_user = session.execute(stmt_verify).scalars().one_or_none()    
    print(f"Verification find: {deleted_user}")
    print("--- DELETE complete ---")

print("--- CRUD TEST FINISHED ---")