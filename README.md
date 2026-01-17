# loto
lucky draws

## Como usar

1. Configure as variáveis de ambiente no arquivo `.env` com as credenciais do banco de dados PostgreSQL.
2. Execute o script `main.py` para importar os dados do CSV `sorteios_lotofacil.csv` para a tabela `lotofacil` no banco de dados.

### Comando para executar a importação:
```bash
python main.py
```

3. Execute o script `populate_sequences.py` para criar e popular a tabela de sequências:
```bash
python populate_sequences.py
```

4. Para visualizar os indicadores, execute a aplicação web:
```bash
python app.py
```

Acesse http://127.0.0.1:5000/ no navegador para ver os números mais sorteados, sequências repetidas e co-ocorrências de sequências.

Certifique-se de que o banco de dados `loto` existe e que as credenciais estão corretas.
