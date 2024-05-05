import sqlite3

def connect():
    return sqlite3.connect('coins.db')

def create_table():
    ...