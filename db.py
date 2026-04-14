import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="currency_user",         
        password="1234",   
        database="currency_db"
    )