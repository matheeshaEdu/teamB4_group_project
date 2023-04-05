from werkzeug.security import generate_password_hash, check_password_hash

# get user password
pwd = input("Enter Your Plain Text: ")
# generate a password hash
hashed_password = generate_password_hash(pwd)

# check if a plain-text password matches the hash
is_valid = check_password_hash(hashed_password, pwd)

if is_valid:
    print(f"Cipher Text: \n{hashed_password}")
else:
    print("Password is not valid")
