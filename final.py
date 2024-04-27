#!/usr/bin/env python3


import click
import sqlite3
import os
import sys
import time
SCHEMA_FILE = 'schema.sql'
DB_NAME = 'database.db'

def read_schema():
    with open(SCHEMA_FILE, 'r') as f:
        return f.read()

@click.group()
def cli():
    pass

@click.command()
def create():
    # Connect to the SQLite database (this will create it if it doesn't exist)
    con = sqlite3.connect(DB_NAME)
    cursor = con.cursor()
    print('Connected to the SQLite database')
    
    # Read the schema file's content
    schema = read_schema()

    # Execute the schema file's commands
    try:
        cursor.executescript(schema)
        click.echo("Database created successfully.")
    except sqlite3.Error as e:
        click.echo(f"An error occurred: {e}")
    finally:
        con.close()

def getdb(create=False):
    if not os.path.exists(DB_NAME):
        if not create:
            print('No database found. Please create the database first.')
            sys.exit(1)
        else:
            create()
    con = sqlite3.connect(DB_NAME)
    con.execute('PRAGMA foreign_keys = ON')
    return con

@click.command()
@click.argument('email')
@click.argument('name') #arguements for following function 

def adduser(email,name):
     with getdb() as con:
        print('Creating user with name and email address:', email," and ",name)
        cursor = con.cursor()
        cursor.execute('INSERT INTO Users (email,name) VALUES (?,?)', (email,name))
        id = cursor.lastrowid
        print(f'Inserted with id={id}')


@click.command() #add listing / address to address table click 
@click.argument('username')
@click.argument('title')
@click.argument('description')
@click.argument('xcoordinate')
@click.argument('ycoordinate')
def addListing(username,title, description, xcoordinate, ycoordinate):
    userId = verifyUser(username)
    if userId is not None:
        with getdb() as con:
            print('Creating Listing with title:', title, 'location at:', xcoordinate, " " , ycoordinate)
            cursor = con.cursor()
            cursor.execute('''INSERT INTO Listings (userId, title, description)
                    VALUES (?,?,?)''', (userId, title, description))
            id = cursor.lastrowid #?
            cursor.execute('''INSERT INTO Locations (listingId, x, y) VALUES (?,?,?)''', (id, xcoordinate, ycoordinate))
            print(f'Inserted with id={id}')
    else:
        print('Error: No user found with name:', username)

@click.command()
@click.argument('x')
@click.argument('y')
@click.argument('radius')
def searchRadius(x,y,radius):
    print('Searching for listings within radius:', radius, 'from location:', x, y)
    with getdb() as con:
        cursor = con.cursor ()
        cursor.execute('''
            SELECT Listings.id, Listings.title, Listings.description, Locations.x, Locations.y, SQRT((Locations.x - ?) * (Locations.x - ?) + (Locations.y - ?) * (Locations.y - ?)) AS distance
            FROM Listings
            JOIN Locations ON Listings.id = Locations.listingId
            WHERE ((Locations.x - ?) * (Locations.x - ?) + (Locations.y - ?) * (Locations.y - ?)) < ? * ?
            ''', (x,x,y,y,x, x, y, y, radius, radius))
        rows = cursor.fetchall()
        print('Found', len(rows), 'listings within radius:', radius, 'from location:', x, y)
        for row in rows:
            print(f"""
                Id: {row[0]}
                Title: {row[1]}
                Description: {row[2]}
                xCoordinate: {row[3]}
                yCoordinate: {row[4]}
                Distance: {row[5]} Cordinates
            """)

@click.command()
@click.argument('username')
def userlistings(username):
    userId = verifyUser(username)
    if userId is not None:
        print('Listing all listings for user:', userId)
        with getdb() as con:
            cursor = con.cursor()
            cursor.execute('SELECT * FROM Listings WHERE userId = ?', (userId,))
            rows = cursor.fetchall()
            print('Found', len(rows), 'listings for user:', userId)
            for row in rows:
                print(f"""
                    Id: {row[0]}
                    Title: {row[2]}
                    Description: {row[3]}
                """)
    else:
        print('Error: No user found with name:', username)

@click.command()
@click.argument('username')
@click.argument('listingid')
def delete(userName, listingid):
    userId = verifyUser(userName)
    if userId is not None:
        print('Deleting listing:', listingid, 'for user:', userId)
        with getdb() as con:
            cursor = con.cursor()
            cursor.execute('DELETE FROM Listings WHERE id = ? AND userId = ?', (listingid, userId))
            if cursor.rowcount == 0:
                print('No listing found with id:', listingid, 'for user:', userId)
            else:
                print('Deleted listing with id:', listingid, 'for user:', userId)
    else:
        print('Error: No user found with name:', userName)

@click.command()
@click.argument('username')
@click.argument('listingid')
@click.argument('day1')
@click.argument('day2')
def reserve(username, listingid, day1, day2):
    userId = verifyUser(username)
    if userId is not None:
        print('Reserving listing:', listingid, 'for user:', userId, 'from:', day1, 'to:', day2)
        with getdb() as con:
            cursor = con.cursor()
            cursor.execute('''
                SELECT * FROM Reservations 
                WHERE listingId = ? AND NOT (day2 < ? OR day1 > ?)
            ''', (listingid, day1, day2))
            overlapping_reservations = cursor.fetchall()
            if overlapping_reservations:
                print("Error: There are overlapping reservations.")
            else:
                # Code to insert the new reservation
                cursor.execute('''
                    INSERT INTO Reservations (userId, listingId, day1, day2)
                    VALUES (?,?,?,?)
                ''', (userId, listingid, day1, day2))
                id = cursor.lastrowid
                print(f'Inserted with id={id} for user:{userId} and listing:{listingid}')
    else:
        print('Error: No user found with name:', username)


@click.command()
@click.argument('username')
def userreservations(username):
    userId = verifyUser(username)
    if userId is not None:
        print('Listing all reservations for user:', userId)
        with getdb() as con:
            cursor = con.cursor()
            cursor.execute('SELECT * FROM Reservations WHERE userId = ?', (userId,))
            rows = cursor.fetchall()
            print('Found', len(rows), 'reservations for user:', userId)
            for row in rows:
                print(f"""
                    Id: {row[0]}
                    ListingId: {row[2]}
                    Day1: {row[3]}
                    Day2: {row[4]}
                """)
    else:
        print('Error: No user found with name:', username)

@click.command()
@click.argument('listingid')
def listingreservations(listingid):
    print('Listing all reservations for listing:', listingid)
    with getdb() as con:
        cursor = con.cursor()
        cursor.execute('SELECT * FROM Reservations WHERE listingId = ?', (listingid,))
        rows = cursor.fetchall()
        print('Found', len(rows), 'reservations for listing:', listingid)
        for row in rows:
            print(f"""
                Id: {row[0]}
                UserId: {row[1]}
                Day1: {row[3]}
                Day2: {row[4]}
            """)

@click.command()
@click.argument('username')
@click.argument('listingid')
def cancel(username, listingid):
    userId = verifyUser(username)
    if userId is not None:
        print('Canceling reservation for listing:', listingid, 'for user:', userId)
        with getdb() as con:
            cursor = con.cursor()
            cursor.execute('DELETE FROM Reservations WHERE listingId = ? AND userId = ?', (listingid, userId))
            if cursor.rowcount == 0:
                print('No reservation found for listing:', listingid, 'for user:', userId)
            else:
                print('Canceled reservation for listing:', listingid, 'for user:', userId)
    else:
        print('Error: No user found with name:', username)

@click.command()
@click.argument('username')
@click.argument('listingid')
@click.argument('rating')
@click.argument('comment')
def rate(username, listingid, rating, comment):
    userId = verifyUser(username)
    if userId is not None:
        print('Rating listing:', listingid, 'for user:', userId, 'with rating:', rating, 'and comment:', comment)
        with getdb() as con:
            cursor = con.cursor()
            cursor.execute('''
                INSERT INTO Ratings (userId, listingId, rating, comment)
                VALUES (?,?,?,?)
            ''', (userId, listingid, rating, comment))
            id = cursor.lastrowid
            print(f'Inserted with id={id} for user:{userId} and listing:{listingid}')
    else:
        print('Error: No user found with name:', username)

@click.command()
@click.argument('listingid')
def listingrating(listingid):
    print('Listing all ratings for listing:', listingid)
    with getdb() as con:
        cursor = con.cursor()
        cursor.execute('SELECT * FROM Ratings WHERE listingId = ?', (listingid,))
        rows = cursor.fetchall()
        print('Found', len(rows), 'ratings for listing:', listingid)
        for row in rows:
            print(f"""
                Id: {row[0]}
                UserId: {row[1]}
                Rating: {row[3]}
                Comment: {row[4]}
            """)

@click.command()
@click.argument('x')
@click.argument('y')
def searchAll(x,y):
    print('Searching for listings near location:', x, y)
    with getdb() as con:
        cursor = con.cursor()
        cursor.execute('''
            SELECT Listings.*, SQRT((Locations.x - ?)*(Locations.x - ?) + (Locations.x - ?)*(Locations.x - ?)) AS distance
            FROM Listings
            JOIN Locations ON Listings.id = Locations.listingId
            ORDER BY distance
            ''', (x,x,y, y))
        rows = cursor.fetchall()
        print('Found', len(rows), 'listings near location:', x, y)
        for row in rows:
            print(f"""
                Id: {row[0]}
                Title: {row[1]}
                Description: {row[2]}
                xCoordinate: {row[3]}
                yCoordinate: {row[4]}
            """)


def verifyUser(userName):
    with getdb() as con:
        cursor = con.cursor()
        cursor.execute('SELECT id FROM Users WHERE name = ?', (userName,))
        rows = cursor.fetchall()
        if len(rows) == 0:
            print(f'Error: No user found with name: {userName}')
            sys.exit(1)
        return rows[0][0]






# Adding commands to the click group
cli.add_command(create)
cli.add_command(adduser)
cli.add_command(addListing)
cli.add_command(searchRadius)
cli.add_command(searchAll)
cli.add_command(userlistings)
cli.add_command(delete)
cli.add_command(reserve)
cli.add_command(userreservations)
cli.add_command(listingreservations)
cli.add_command(cancel)
cli.add_command(rate)
cli.add_command(listingrating)


cli()
