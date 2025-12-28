
temp = 92
cpu_load = 45
memory_use = 78

# Use a custom separator to create a clean, pipeline-style output

print("STATUS", temp, cpu_load, memory_use)
print("STATUS", temp, cpu_load, memory_use, sep=" | ")