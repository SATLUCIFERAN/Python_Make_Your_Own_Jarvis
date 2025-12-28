

# WARNING: This captures the variable 'i', not the value!
funcs = [lambda: i for i in range(3)] 
print([f() for f in funcs])    


# FIX: 'i=i' binds the value of 'i' at the time the lambda is defined.
fixed_funcs = [lambda i=i: i for i in range(3)]
print([f() for f in fixed_funcs]) # Output: [0, 1, 2]                                                        # Output: [2, 2, 2]