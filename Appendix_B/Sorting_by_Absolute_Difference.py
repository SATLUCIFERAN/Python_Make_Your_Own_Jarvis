
target_latency = 25
network_pings = [28, 15, 26, 35, 23]

# Key: Calculate the absolute distance from the target (25).
network_pings.sort(key=lambda ping: abs(ping - target_latency), reverse=True)

# Jarvis Output: The most anomalous pings are first!
print(network_pings)
# Output: [15, 35, 28, 23, 26]