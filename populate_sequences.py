import os
import psycopg2
from dotenv import load_dotenv
from itertools import combinations
from collections import defaultdict

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def create_tables():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    for k in range(10, 16):
        table_name = f"repeated_{k}"
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            combination TEXT,
            frequency INTEGER,
            details TEXT
        );
        """)
    conn.commit()
    cursor.close()
    conn.close()

def populate_repeated_combinations():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = "SELECT concurso, data, bola1, bola2, bola3, bola4, bola5, bola6, bola7, bola8, bola9, bola10, bola11, bola12, bola13, bola14, bola15 FROM lotofacil;"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    for k in range(10, 16):
        combo_details = defaultdict(list)
        for row in rows:
            concurso, data, *bolas = row
            bolas_sorted = sorted(bolas)
            for combo in combinations(bolas_sorted, k):
                combo_details[combo].append((concurso, data))
        
        repeated = {combo: details for combo, details in combo_details.items() if len(details) > 1}
        sorted_repeated = sorted(repeated.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        table_name = f"repeated_{k}"
        cursor.execute(f"DELETE FROM {table_name};")  # Limpar
        for combo, details in sorted_repeated:
            combo_str = '-'.join(map(str, combo))
            freq = len(details)
            details_str = ', '.join([f"{c}({d})" for c, d in details])
            cursor.execute(f"INSERT INTO {table_name} (combination, frequency, details) VALUES (%s, %s, %s);", (combo_str, freq, details_str))
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == '__main__':
    create_tables()
    populate_repeated_combinations()
    print("Tabelas de combinações repetidas criadas e populadas!")