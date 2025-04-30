import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

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

def create_dimension_tables(engine):
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_attack_type (
                attack_type_id SERIAL PRIMARY KEY,
                attack_type VARCHAR(100) UNIQUE
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_severity (
                severity_id SERIAL PRIMARY KEY,
                severity VARCHAR(50) UNIQUE
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_destination_port (
                port_id SERIAL PRIMARY KEY,
                destination_port INTEGER UNIQUE
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_timestamp (
                timestamp_id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP UNIQUE,
                year INTEGER,
                month INTEGER,
                day INTEGER,
                hour INTEGER
            )
        """))

        conn.commit()
        print("Tabelas de dimensões criadas com sucesso!")

def normalize_dimensions():
    engine = create_database_connection()
    if not engine:
        return

    try:
        create_dimension_tables(engine)

        print("Lendo dados da tabela raw...")
        df = pd.read_sql("SELECT * FROM raw_cybersecurity_attacks", engine)
        print(f"Total de registros lidos: {len(df)}")

        with engine.connect() as conn:
            print("Normalizando dimensão attack_type...")
            attack_types = df['Attack Type'].unique()
            for attack_type in attack_types:
                conn.execute(
                    text("INSERT INTO dim_attack_type (attack_type) VALUES (:attack_type) ON CONFLICT DO NOTHING"),
                    {"attack_type": attack_type}
                )

            print("Normalizando dimensão severity...")
            severities = df['Severity Level'].unique()
            for severity in severities:
                conn.execute(
                    text("INSERT INTO dim_severity (severity) VALUES (:severity) ON CONFLICT DO NOTHING"),
                    {"severity": severity}
                )

            print("Normalizando dimensão destination_port...")
            ports = df['Destination Port'].unique()
            for port in ports:
                try:
                    port_int = int(port)
                    conn.execute(
                        text("INSERT INTO dim_destination_port (destination_port) VALUES (:port) ON CONFLICT DO NOTHING"),
                        {"port": port_int}
                    )
                except (ValueError, TypeError):
                    print(f"Aviso: Porta inválida encontrada: {port}")

            print("Normalizando dimensão timestamp...")
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            for _, row in df.iterrows():
                conn.execute(
                    text("""
                        INSERT INTO dim_timestamp
                        (timestamp, year, month, day, hour)
                        VALUES (:timestamp, :year, :month, :day, :hour)
                        ON CONFLICT DO NOTHING
                    """),
                    {
                        "timestamp": row['Timestamp'],
                        "year": row['Timestamp'].year,
                        "month": row['Timestamp'].month,
                        "day": row['Timestamp'].day,
                        "hour": row['Timestamp'].hour
                    }
                )

            conn.commit()
            print("Dados normalizados e inseridos nas dimensões com sucesso!")

    except Exception as e:
        print(f"Erro ao normalizar dimensões: {str(e)}")

if __name__ == "__main__":
    normalize_dimensions()