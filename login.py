import sqlite3
import hashlib

# Connect to sqlite
conn = sqlite3.connect("users.db")

# Create a cursor object
cursor = conn.cursor()

# Asks the user for their username and password
user = input("Username: ")
rawPassword = input("Password: ")
# Encodes the password into bytes
bytePassword = rawPassword.encode('utf-8')
# Hashes the encoded password for comparison
hashPassword = hashlib.sha256(bytePassword).hexdigest()


# Selects the hashed password of the user in the database
cursor.execute("SELECT password_hash FROM Users WHERE USERNAME = ?", (user,))

# Fetches the correct hashed password
validUser = cursor.fetchone()

# Checks if a field is fetched
if validUser is None:
    print("User not found!")
else:
    # Gets the correct hashed password from the list
    correctHash = validUser[0]

    # Checks if the correct hashed password matches the entered password
    if hashPassword == correctHash:
        print("Login Successful!")
    else:
        print("Login Failed!")




# Closes the cursor object and connection
cursor.close()
conn.close()