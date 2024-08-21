import secrets

# Generate a 64-character random secret key
secret_key = secrets.token_hex(32)

with open('.env', 'w') as file:
    file.write(F"SECRET_KEY={secret_key}\n")

print("Secret key generated and saved to .env file.")
