
# WARNING: This is the common mistake!
process_ids = [9845, 102, 3401, 77, 9845]

# The sorted result is assigned to 'sorted_ids'
sorted_ids = process_ids.sort() 

print(sorted_ids) 
# Output: None  <-- Jarvis is now holding nothing!
print(process_ids) 
# Output: [77, 102, 3401, 9845, 9845] <-- The original list was sorted successfully!