from flask import Flask, render_template
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')

def get_most_frequent_numbers():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = """
    SELECT numero, COUNT(*) as frequencia
    FROM (
        SELECT bola1 as numero FROM lotofacil
        UNION ALL SELECT bola2 FROM lotofacil
        UNION ALL SELECT bola3 FROM lotofacil
        UNION ALL SELECT bola4 FROM lotofacil
        UNION ALL SELECT bola5 FROM lotofacil
        UNION ALL SELECT bola6 FROM lotofacil
        UNION ALL SELECT bola7 FROM lotofacil
        UNION ALL SELECT bola8 FROM lotofacil
        UNION ALL SELECT bola9 FROM lotofacil
        UNION ALL SELECT bola10 FROM lotofacil
        UNION ALL SELECT bola11 FROM lotofacil
        UNION ALL SELECT bola12 FROM lotofacil
        UNION ALL SELECT bola13 FROM lotofacil
        UNION ALL SELECT bola14 FROM lotofacil
        UNION ALL SELECT bola15 FROM lotofacil
    ) as bolas
    GROUP BY numero
    ORDER BY frequencia DESC
    LIMIT 25;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_longest_sequences():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = "SELECT concurso, data, bola1, bola2, bola3, bola4, bola5, bola6, bola7, bola8, bola9, bola10, bola11, bola12, bola13, bola14, bola15 FROM lotofacil ORDER BY concurso DESC;"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    from collections import defaultdict
    seq_count = defaultdict(int)
    
    for row in rows:
        concurso, data, *bolas = row
        bolas_sorted = sorted(bolas)
        i = 0
        while i < len(bolas_sorted) - 1:
            start = i
            while i < len(bolas_sorted) - 1 and bolas_sorted[i+1] == bolas_sorted[i] + 1:
                i += 1
            seq_len = i - start + 1
            if seq_len >= 3:
                seq = tuple(bolas_sorted[start:start+seq_len])
                seq_count[seq] += 1
            i += 1
    
    # Ordenar por frequência DESC
    sorted_seq = sorted(seq_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_seq[:20]  # Top 20 sequências

def get_sequence_cooccurrences():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = """
    SELECT s1.seq, s2.seq, COUNT(*) as cooc
    FROM sequences s1
    JOIN sequences s2 ON s1.concurso = s2.concurso AND s1.seq < s2.seq
    GROUP BY s1.seq, s2.seq
    ORDER BY cooc DESC
    LIMIT 20;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

from itertools import combinations

def get_repeated_combinations(k):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = "SELECT bola1, bola2, bola3, bola4, bola5, bola6, bola7, bola8, bola9, bola10, bola11, bola12, bola13, bola14, bola15 FROM lotofacil;"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    from collections import defaultdict
    combo_count = defaultdict(int)
    
    for row in rows:
        bolas = sorted(row)
        for combo in combinations(bolas, k):
            combo_count[combo] += 1
    
    # Filtrar apenas >1
    repeated = {combo: count for combo, count in combo_count.items() if count > 1}
    # Ordenar por count DESC
    sorted_repeated = sorted(repeated.items(), key=lambda x: x[1], reverse=True)
    return sorted_repeated[:10]  # Top 10 por k

@app.route('/')
def index():
    numbers = get_most_frequent_numbers()
    sequences = get_longest_sequences()
    cooccurrences = get_sequence_cooccurrences()
    repeated_15 = get_repeated_combinations(15)
    repeated_14 = get_repeated_combinations(14)
    repeated_13 = get_repeated_combinations(13)
    repeated_12 = get_repeated_combinations(12)
    repeated_11 = get_repeated_combinations(11)
    repeated_10 = get_repeated_combinations(10)
    return render_template('index.html', numbers=numbers, sequences=sequences, cooccurrences=cooccurrences,
                           repeated_15=repeated_15, repeated_14=repeated_14, repeated_13=repeated_13,
                           repeated_12=repeated_12, repeated_11=repeated_11, repeated_10=repeated_10)

if __name__ == '__main__':
    app.run(debug=True)