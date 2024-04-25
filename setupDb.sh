#!/bin/bash
rm -f database.db
# Path to your Python script
PYTHON_SCRIPT="./social.py"

# Create the database and schema
python3 $PYTHON_SCRIPT create
python3 $PYTHON_SCRIPT adduser "test" "test"
python3 $PYTHON_SCRIPT addaccount "test" "test"
python3 $PYTHON_SCRIPT createpost "test" "test" "test"
python3 $PYTHON_SCRIPT follow "test" "test"


$(python3 $PYTHON_SCRIPT follow "test" "test2")  # Store the id in a variable


# Number of users to add
NUM_USERS=20
# Add users and accounts in a loop
for i in $(seq 1 $NUM_USERS); do
    # Generate a unique username and email for each user
    USERNAME="User${i}"
    EMAIL="user${i}@example.com"
    
    # Add user
    python3 $PYTHON_SCRIPT adduser "$USERNAME" "$EMAIL"
    
    # Add account for user
    python3 $PYTHON_SCRIPT addaccount "${USERNAME}" "$EMAIL" 
    python3 $PYTHON_SCRIPT follow "${USERNAME}" "test"
    python3 $PYTHON_SCRIPT comment "${USERNAME}" "1" "test"  # Use the stored id
    
    # Create a post for each user
    TITLE="${USERNAME}'s Post"
    CONTENT="This is a post by ${USERNAME}."
    id=$(python3 $PYTHON_SCRIPT createpost "${USERNAME}" "$TITLE" "$CONTENT")  # Store the id in a variable
    echo "Inserted with id=$id"
done

echo "Database populated with $NUM_USERS users, accounts, and posts."
