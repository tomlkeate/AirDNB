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
@click.argument('name')
@click.argument('email')
def adduser(name, email):
     with getdb() as con:
        print('Creating user with name and email address:', name," and ",email)
        cursor = con.cursor()
        cursor.execute('INSERT INTO Users (name,email) VALUES (?,?)', (name,email))
        id = cursor.lastrowid
        print(f'Inserted with id={id}')

@click.command()
@click.argument('username')
@click.argument('email')
def addaccount(email, username):
     with getdb() as con:
        print('Creating account with username:', username, 'for email:', email)
        cursor = con.cursor()
        cursor.execute('''INSERT INTO Accounts (userId, userName)
                        VALUES ((SELECT id FROM Users WHERE email = ?), ?)''', (email, username))
        id = cursor.lastrowid
        print(f'Inserted with id={id}')

@click.command()
@click.argument('username')
@click.argument('title')
@click.argument('content')
def createpost(username, title, content):
     with getdb() as con:
        cursor = con.cursor()
        print('Creating post with title:', title, 'for user:', username)
        cursor.execute('''SELECT id FROM Accounts WHERE username = ?''', (username,))
        user_id = cursor.fetchone()
        if user_id is None:
            print('User does not exist.')
            return
        cursor.execute('''INSERT INTO Posts (posterId, title, textBody)
                        VALUES ((SELECT id FROM accounts WHERE username = ?), ?, ?)''', (username, title, content))
        id = cursor.lastrowid
        print(f'Inserted with id={id}')
        return id



@click.command()
@click.argument('username')
def feed(username):
    print('Listing Feed for user:', username)

    with getdb() as con:
        cursor = con.cursor()
        cursor.execute('''
                SELECT DISTINCT Posts.*, COUNT(Likes.postId) AS likes, Accounts.userName,
                GROUP_CONCAT(c.combined_comments) AS comments
                FROM Posts
                LEFT JOIN Likes ON Posts.id = Likes.postId
                LEFT JOIN Accounts ON Posts.posterId = Accounts.userId
                LEFT JOIN (
                    SELECT Comments.postId, GROUP_CONCAT(cAc.userName || ': ' || Comments.textBody, ', ') AS combined_comments
                    FROM Comments
                    JOIN Accounts AS cAc ON Comments.commenterId = cAc.userId
                    GROUP BY Comments.postId
                ) AS c ON Posts.id = c.postId
                WHERE Posts.posterId IN (
                    SELECT followeeId FROM Follows WHERE followerId = (
                        SELECT id FROM Accounts WHERE userName = ?
                    )
                )
                GROUP BY Posts.id

        ''', (username,))
        rows = cursor.fetchall()
        for row in rows:
            print(f"""
                UserName: {row[6]}
                Id: {row[0]}
                Title: {row[1]}
                TextBody: {row[2]}
                Date: {row[3]}
                Likes: {row[5]}
                Comments: {row[7]}
            """)


@click.command()
@click.argument('username')
def myposts(username):
    print('Listing posts for user:', username)

    with getdb() as con:
        cursor = con.cursor()
        cursor.execute('''SELECT * FROM Posts WHERE posterId = (SELECT id FROM accounts WHERE userName = ?)''', (username,))
        rows = cursor.fetchall()
        for row in rows:
            print(row)

@click.command()
@click.argument('username')
@click.argument('postid')
def deletepost(username, postid):
    print('Deleting post:', postid, 'for user:', username)
    
    with getdb() as con:
        cursor = con.cursor()

        cursor.execute('''
            SELECT id FROM Posts WHERE id = ? AND posterId = (
                SELECT id FROM Accounts WHERE userName = ?
            )
        ''', (postid, username))
        post = cursor.fetchone()
        if post is None:
            print('This is not your post')
            return

        cursor.execute('DELETE FROM Likes WHERE postId = ?', (postid,))
        cursor.execute('DELETE FROM Comments WHERE postId = ?', (postid,))
        cursor.execute('DELETE FROM Follows WHERE followeeId = ?', (postid,))

        cursor.execute('DELETE FROM Posts WHERE id = ?', (postid,))
        print('Deleted successfully.')


@click.command()
@click.argument('username')
@click.argument('followusername')
def follow(username, followusername):
     with getdb() as con:
        cursor = con.cursor()
        cursor.execute('''SELECT id FROM Accounts WHERE userName = ?''', (username,))
        user_id = cursor.fetchone()
        if user_id is None:
            print('follower does not exist.')
            return
        cursor.execute('''SELECT * FROM Accounts WHERE userName = ?''', (followusername,))
        followId=cursor.fetchone()
        if followId is None:
            print('followee does not exist.')
            return
        print('Following user:', followusername, 'with id:', username)
        cursor = con.cursor()
        cursor.execute('''INSERT INTO Follows (followerId, followeeId) VALUES ((SELECT id FROM Accounts WHERE userName = ?), (SELECT id FROM Accounts WHERE userName = ?))''', (username, followusername))
        id = cursor.lastrowid
        print(f'Inserted with id={id}')
        cursor.execute('''SELECT DISTINCT Accounts.userName, Accounts.id
                        FROM Follows
                        JOIN Accounts ON Follows.followerId = Accounts.id
                        WHERE Follows.followeeId = (SELECT id FROM Accounts WHERE userName = ?)
                        LIMIT 10''', (followusername,))
        rows = cursor.fetchall()
        print('Suggested users to follow:')
        for row in rows:
            print(f'UserName: {row[0]} UserId: {row[1]} ')

@click.command()
@click.argument('username')
@click.argument('unfollowusername')
def unfollow(username, unfollowusername):
     with getdb() as con:
        cursor = con.cursor()
        cursor.execute('''SELECT id FROM Accounts WHERE userName = ?''', (username,))
        user_id = cursor.fetchone()
        unfollowId=cursor.execute('''SELECT * FROM Accounts WHERE userName = ?''', (unfollowusername,))
        if user_id is None:
            print('User does not exist.')
            return
        if unfollowId is None:
            print('User to unfollow does not exist.')
            return
        print('Unfollowing user:', username, 'with id:', unfollowusername)
        cursor.execute('''DELETE FROM Follows WHERE followerId = (SELECT id FROM accounts WHERE username = ?) 
                          AND followeeId = (SELECT userId FROM accounts WHERE username = ?)''', (username, unfollowusername))
        print('Unfollowed successfully.')

@click.command()
@click.argument('username')
def listfollows(username):
    print('Listing follows for user:', username)
    with getdb() as con:
        cursor = con.cursor()
        cursor.execute('''SELECT Accounts.userName
                        FROM Follows
                        LEFT JOIN Accounts ON Follows.followeeId = Accounts.userId
                        WHERE Follows.followerId = (SELECT userId FROM accounts WHERE userName = ?)''', (username,))
        rows = cursor.fetchall()
        for row in rows:
            print(row)

@click.command()
@click.argument('searchuser')
def searchuser(searchuser):
    print('Searching for user:', searchuser)
    with getdb() as con:
        cursor = con.cursor()
        username = "%" + searchuser + "%"
        cursor.execute('''SELECT * FROM Accounts WHERE userName LIKE ?''', (username,))
        rows = cursor.fetchall()
        print('Found the following users:')
        for row in rows:
            print(row)
    

@click.command()
@click.argument('username')
@click.argument('postid')
def like(username, postid):
    print('Liking post:', postid, 'for user:', username)
    with getdb() as con:
        cursor = con.cursor()
        cursor.execute('''SELECT * FROM Likes WHERE postId = ? AND userId = (SELECT id FROM Accounts WHERE userName = ?)''', (postid, username))
        row = cursor.fetchone()
        if row is not None:
            print('You have already liked this post.')
            return
        cursor.execute('''INSERT INTO Likes (postId, userId)
                        VALUES (?, (SELECT id FROM Accounts WHERE userName = ?))''', (postid, username))
        id = cursor.lastrowid
        print(f'Inserted with id={id}')


@click.command()
@click.argument('username')
@click.argument('postid')
@click.argument('comment')
def comment(username, postid, comment):
    print('Commenting on post:', postid, 'for user:', username, 'comment:', comment)
    with getdb() as con:
        cursor = con.cursor()
        # cursor.execute('''SELECT * FROM Likes WHERE postId = ? AND userId = (SELECT id FROM Accounts WHERE userName = ?)''', (postid, username))
        # row = cursor.fetchone()
        # if row is None:
        #     print('You can only comment on posts that you have liked.')
        #     return
        cursor.execute('''INSERT INTO Comments (textBody, commenterId, postId)
                        VALUES (?, (SELECT id FROM Accounts WHERE userName = ?), ?)''', (comment, username, postid))
        id = cursor.lastrowid
        print(f'Inserted with id={id}')


# Adding commands to the click group
cli.add_command(feed)
cli.add_command(create)
cli.add_command(createpost)
cli.add_command(adduser)
cli.add_command(addaccount)
cli.add_command(follow)
cli.add_command(searchuser)
cli.add_command(unfollow)
cli.add_command(listfollows)
cli.add_command(myposts)
cli.add_command(deletepost)
cli.add_command(like)
cli.add_command(comment)


cli()
