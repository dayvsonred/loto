from flask import Flask, render_template, request
import psycopg2
from dotenv import load_dotenv
import os
from itertools import combinations
from collections import defaultdict
import requests

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
    table_name = f"repeated_{k}"
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    if count == 0:
        # Calcular e inserir
        query = "SELECT concurso, data, bola1, bola2, bola3, bola4, bola5, bola6, bola7, bola8, bola9, bola10, bola11, bola12, bola13, bola14, bola15 FROM lotofacil;"
        cursor.execute(query)
        rows = cursor.fetchall()
        combo_details = defaultdict(list)
        for row in rows:
            concurso, data, *bolas = row
            bolas_sorted = sorted(bolas)
            for combo in combinations(bolas_sorted, k):
                combo_details[combo].append((concurso, data))
        repeated = {combo: details for combo, details in combo_details.items() if len(details) > 1}
        sorted_repeated = sorted(repeated.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for combo, details in sorted_repeated:
            combo_str = '-'.join(map(str, combo))
            freq = len(details)
            details_str = ', '.join([f"{c}({d})" for c, d in details])
            cursor.execute(f"INSERT INTO {table_name} (combination, frequency, details) VALUES (%s, %s, %s);", (combo_str, freq, details_str))
        conn.commit()
    
    # Buscar
    cursor.execute(f"SELECT combination, frequency, details FROM {table_name} ORDER BY frequency DESC;")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    # Parse details back to list
    parsed = []
    for combo_str, freq, details_str in results:
        combo = tuple(map(int, combo_str.split('-')))
        details = []
        if details_str:
            for item in details_str.split(', '):
                if '(' in item and ')' in item:
                    c, d = item.split('(')
                    d = d.rstrip(')')
                    details.append((int(c), d))
        parsed.append((combo, freq, details))
    return parsed

def get_last_draws(n):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = "SELECT concurso, data, bola1, bola2, bola3, bola4, bola5, bola6, bola7, bola8, bola9, bola10, bola11, bola12, bola13, bola14, bola15 FROM lotofacil ORDER BY concurso DESC LIMIT %s;"
    cursor.execute(query, (n,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

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
    last_draws = get_last_draws(15)
    return render_template('index.html', numbers=numbers, sequences=sequences, cooccurrences=cooccurrences,
                           repeated_15=repeated_15, repeated_14=repeated_14, repeated_13=repeated_13,
                           repeated_12=repeated_12, repeated_11=repeated_11, repeated_10=repeated_10, last_draws=last_draws)

@app.route('/search')
def search():
    sequence_str = request.args.get('sequence', '')
    if not sequence_str:
        return render_template('search.html', results=None, query='')
    
    try:
        numbers = set(map(int, sequence_str.split('-')))
        if not numbers or any(n < 1 or n > 25 for n in numbers):
            raise ValueError
    except ValueError:
        return render_template('search.html', results=None, query=sequence_str, error="Sequência inválida. Use números de 1 a 25 separados por -.")
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = "SELECT concurso, data, bola1, bola2, bola3, bola4, bola5, bola6, bola7, bola8, bola9, bola10, bola11, bola12, bola13, bola14, bola15 FROM lotofacil ORDER BY concurso DESC;"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    results = []
    for row in rows:
        concurso, data, *bolas = row
        bolas_set = set(bolas)
        if numbers.issubset(bolas_set):
            results.append((concurso, data, sorted(bolas)))
    
    return render_template('search.html', results=results, query=sequence_str)

@app.route('/fetch_latest')
def fetch_latest():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(concurso) FROM lotofacil;")
    max_concurso = cursor.fetchone()[0]
    
    if max_concurso is None:
        cursor.close()
        conn.close()
        return render_template('latest.html', error="Nenhum concurso encontrado na base de dados.")
    
    next_concurso = max_concurso + 1
    url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{next_concurso}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        numero = data.get("numero")
        data_str = data.get("dataApuracao")
        lista_dezenas = data.get("listaDezenas", [])
        
        if numero and data_str and lista_dezenas:
            from datetime import datetime
            data_sorteio = datetime.strptime(data_str, '%d/%m/%Y').date()
            bolas = [int(d) for d in lista_dezenas]
            
            # Insert into lotofacil
            insert_query = """
            INSERT INTO lotofacil (concurso, data, bola1, bola2, bola3, bola4, bola5, bola6, bola7, bola8, bola9, bola10, bola11, bola12, bola13, bola14, bola15)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (concurso) DO NOTHING;
            """
            cursor.execute(insert_query, (numero, data_sorteio, *bolas))
            
            # Clear cached tables
            cursor.execute("DELETE FROM sequences;")
            for k in range(10, 16):
                cursor.execute(f"DELETE FROM repeated_{k};")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return render_template('latest.html', concurso=numero, dezenas=lista_dezenas)
        else:
            cursor.close()
            conn.close()
            return render_template('latest.html', error=f"Dados incompletos para o sorteio {next_concurso}")
    else:
        cursor.close()
        conn.close()
        return render_template('latest.html', error=f"sorteio não encontrado numero {next_concurso}")

if __name__ == '__main__':
    app.run(debug=True)