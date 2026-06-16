import mysql.connector

cn = mysql.connector.connect(
    user = 'root',
    password = '180507',
    host = '127.0.0.1',
    database = 'quizgen_ia',
    port = 3306
)