#!/bin/bash
rm -f database.db
# Path to your Python script
PYTHON_SCRIPT="./final.py"

# Create the database and schema
python3 $PYTHON_SCRIPT create

# Number of users to add
NUM_USERS=20

# Add users in a loop
for i in $(seq 1 $NUM_USERS); do
    # Generate a unique username and email for each user
    USERNAME="User${i}"
    EMAIL="user${i}@example.com"
    
    # Add user
    python3 $PYTHON_SCRIPT adduser "$EMAIL" "$USERNAME"
    
    # Add listing for each user
    TITLE="${USERNAME}'s Listing"
    DESCRIPTION="This is a listing by ${USERNAME}."
    XCOORDINATE=$(((RANDOM % 100) + 1))
    YCOORDINATE=$(((RANDOM % 100) + 1))
    echo "Adding listing for $USERNAME at ($XCOORDINATE, $YCOORDINATE)"
    python3 $PYTHON_SCRIPT addlisting "$USERNAME" "$TITLE" "$DESCRIPTION" "$XCOORDINATE" "$YCOORDINATE"
    
    # Add reservation
    DAY1=$(( (RANDOM % 90) + 1))
    DAY2=$(( DAY1 + (RANDOM % 10) + 1))
    python3 $PYTHON_SCRIPT reserve "$USERNAME" "${i}" "$DAY1" "$DAY2"
    
    # Add review
    RATING=$(( (RANDOM % 5) + 1))
    COMMENT="This is a review by ${i}."
    python3 $PYTHON_SCRIPT rate "$USERNAME" "${i}" "$RATING" "$COMMENT"
done

echo "Database populated with $NUM_USERS users, listings, reservations, and reviews."

# commands
# python3 final.py create
# python3 final.py adduser EMAIL USERNAME
# python3 final.py addlisting USERNAME TITLE DESCRIPTION XCOORDINATE YCOORDINATE 
# python3 final.py reserve USERNAME LISTINGID STARTDATE ENDDATE
# python3 final.py search XCOORDINATE YCOORDINATE  RADIUS
# python3 final.py userlistings USERNAME
# python3 final.py delete USERNAME LISTINGID
# python3 final.py reserve USERNAME LISTINGID STARTDATE ENDDATE
# python3 final.py userreservations USERNAME
# python3 final.py listingreservations LISTINGID
# python3 final.py cancel USERNAME LISTINGID
# python3 final.py rate USERNAME LISTINGID RATING COMMENT
# python3 final.py listingrating LISTINGID
# python3 final.py searchday XCOORDINATE YCOORDINATE STARTDATE ENDDATE
# python3 final.py help
