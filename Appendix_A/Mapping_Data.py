
raw_log_sizes_bytes = [1024, 2048, 5120, 4096]
conversion_factor = 1024 # bytes per KB
log_sizes_kb = list(map(lambda byte_size: byte_size / conversion_factor, 
                                                      raw_log_sizes_bytes))

print(f"Log Sizes (KB): {log_sizes_kb}")


# Output: Log Sizes (KB): [1.0, 2.0, 5.0, 4.0]