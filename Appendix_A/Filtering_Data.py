
temperatures = [88, 92, 98, 90, 101, 94]

# The lambda is the filter condition (True if temp > 95)
critical_temps = list(filter(lambda temp: temp > 95, temperatures))

print(f"Critical Readings: {critical_temps}")
# Output: Critical Readings: [98, 101]