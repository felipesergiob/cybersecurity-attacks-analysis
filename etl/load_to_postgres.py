import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pathlib import Path

def create_database_connection():
    load_dotenv()

    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")

    conn_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"

    try:
        engine = create_engine(conn_string)
        print("Conexão com o banco de dados estabelecida com sucesso!")
        return engine
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {str(e)}")
        return None

def load_data_to_postgres():
    engine = create_database_connection()
    if not engine:
        return

    try:
        data_path = Path("data/cybersecurity_attacks.csv")
        if not data_path.exists():
            print("Arquivo de dados não encontrado!")
            return

        print("Lendo arquivo CSV...")
        df = pd.read_csv(data_path)
        print(f"Total de registros lidos: {len(df)}")

        table_name = "raw_cybersecurity_attacks"
        print(f"Carregando dados na tabela {table_name}...")
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"Dados carregados com sucesso na tabela {table_name}!")

    except Exception as e:
        print(f"Erro ao carregar dados: {str(e)}")

if __name__ == "__main__":
    load_data_to_postgres() 