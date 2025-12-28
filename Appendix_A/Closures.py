
def make_offset_function(seed_value):    
    return lambda data_input: data_input + seed_value

key_offset_5 = make_offset_function(5)
key_offset_12 = make_offset_function(12)

print(f"Data 10 processed with offset 5: {key_offset_5(10)}")
print(f"Data 10 processed with offset 12: {key_offset_12(10)}")

# Output: 
# Data 10 processed with offset 5: 15
# Data 10 processed with offset 12: 22