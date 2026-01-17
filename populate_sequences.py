import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def create_sequences_table():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sequences (
        id SERIAL PRIMARY KEY,
        concurso INTEGER REFERENCES lotofacil(concurso),
        seq TEXT
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def populate_sequences():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Limpar tabela
    cursor.execute("DELETE FROM sequences;")
    
    # Pegar todos os sorteios
    cursor.execute("SELECT concurso, bola1, bola2, bola3, bola4, bola5, bola6, bola7, bola8, bola9, bola10, bola11, bola12, bola13, bola14, bola15 FROM lotofacil;")
    rows = cursor.fetchall()
    
    for row in rows:
        concurso, *bolas = row
        bolas_sorted = sorted(bolas)
        i = 0
        while i < len(bolas_sorted) - 1:
            start = i
            while i < len(bolas_sorted) - 1 and bolas_sorted[i+1] == bolas_sorted[i] + 1:
                i += 1
            seq_len = i - start + 1
            if seq_len >= 3:
                seq = '-'.join(map(str, bolas_sorted[start:start+seq_len]))
                cursor.execute("INSERT INTO sequences (concurso, seq) VALUES (%s, %s);", (concurso, seq))
            i += 1
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    create_sequences_table()
    populate_sequences()
    print("Sequências populadas!")