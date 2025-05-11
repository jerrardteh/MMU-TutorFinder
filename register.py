import sqlite3
import hashlib

# Connect to sqlite
conn = sqlite3.connect("users.db")

# Create a cursor object
cursor = conn.cursor()

# SQL command to create the Users table if doesn't exits
create_user_table_query = '''
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    mmuid TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE CHECK(email LIKE '%mmu.edu.my'),
    role TEXT NOT NULL,
    bio TEXT,
    subjects TEXT
);
'''



cursor.execute(create_user_table_query)

# Commits the changes to the database
conn.commit()


fullName = input("Full Name: ")

user = input("Username: ")

# Gets the user's desired password
rawPassword = input("Password: ")
# Encodes the password into bytes
bytePassword = rawPassword.encode("utf-8")
# Password is hashed by hashlib for additional security
hashPassword = hashlib.sha256(bytePassword).hexdigest()

mmuid = input("Enter your ID: ")

# Makes sure email ends in "mmu.edu.my"
validEmail = 0
while validEmail == 0:
    email = input("Email (MUST END IN MMU.EDU.MY!): ")
    smallEmail = email.lower()
    if "mmu.edu.my" in smallEmail:
        validEmail = 1


role = input("Role: ")

bio = input("Bio: ")
subjects = input("Subjects: ")




# Inserts the user's username and hashed password into the Users table
cursor.execute('''INSERT INTO Users (full_name, username, password_hash, mmuid, email, role, bio, subjects) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
               (fullName, user, hashPassword, mmuid, email, role, bio, subjects)
               )

# Commits the changes
conn.commit()


print("Your account has been successfully created!")



# Closes the cursor object and connection
cursor.close()
conn.close()