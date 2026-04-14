import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="currency_user",         
        password="",   
        database="currency_db"
    )