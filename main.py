import os
import csv
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

# Connect to the database
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create table if not exists
create_table_query = """
CREATE TABLE IF NOT EXISTS lotofacil (
    concurso INTEGER PRIMARY KEY,
    data DATE,
    bola1 INTEGER,
    bola2 INTEGER,
    bola3 INTEGER,
    bola4 INTEGER,
    bola5 INTEGER,
    bola6 INTEGER,
    bola7 INTEGER,
    bola8 INTEGER,
    bola9 INTEGER,
    bola10 INTEGER,
    bola11 INTEGER,
    bola12 INTEGER,
    bola13 INTEGER,
    bola14 INTEGER,
    bola15 INTEGER
);
"""
cursor.execute(create_table_query)
conn.commit()

# Read CSV and insert data
with open('sorteios_lotofacil.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter=';')
    next(reader)  # Skip header
    for row in reader:
        concurso = int(row[0])
        data_str = row[1]
        data = datetime.strptime(data_str, '%d/%m/%Y').date()
        bolas = [int(b) for b in row[2:]]
        insert_query = """
        INSERT INTO lotofacil (concurso, data, bola1, bola2, bola3, bola4, bola5, bola6, bola7, bola8, bola9, bola10, bola11, bola12, bola13, bola14, bola15)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (concurso) DO NOTHING;
        """
        cursor.execute(insert_query, (concurso, data, *bolas))

conn.commit()
cursor.close()
conn.close()

print("Dados inseridos com sucesso!")