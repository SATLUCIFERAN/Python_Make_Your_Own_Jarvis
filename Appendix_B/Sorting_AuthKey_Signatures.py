
authkey_signatures = ["Sentinel", "omega", "Viper", "Omega"]

# The key function tells Python: For sorting, convert the string to lowercase first.
authkey_signatures.sort(key=str.lower)

# Jarvis Output: Alphabetical, regardless of capital letters!
print(authkey_signatures)
# Output: ['Omega', 'omega', 'Sentinel', 'Viper']