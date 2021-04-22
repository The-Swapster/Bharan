import sqlite3
connection = sqlite3.connect("bharan.db")
c = connection.cursor()

def create_table():
    c.execute(
        'create table if not exists citizen(uid integer primary key autoincrement, name text, email text unique, age real, address text, aadhar text, longitude integer, latitude integer)'
    )
    c.execute(
        'create table if not exists vaccinestock(hid text primary key, hname text, snumber integer unique, bnumber text)'
    )
    c.execute(
        'create table if not exists vaccineused(hid text primary key, hname text, snumber integer unique, bnumber text)'
    )
    c.execute(
        'create table if not exists vaccineorder(hid text primary key, hname text, qnumber integer)'
    )
    c.execute(
        'create table if not exists vaccineproduce(mid text primary key, snumber integer unique, bnumber text)'
    )
    c.execute(
        'create table if not exists citizenvaccinated(uid integer primary key autoincrement, name text, email text unique, age real, address text, aadhar text)'
    )
    connection.commit()

create_table()
