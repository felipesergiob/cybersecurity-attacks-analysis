import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

def extract_data():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    try:
        csv_path = data_dir / "cybersecurity_attacks.csv"
        if not csv_path.exists():
            print(f"Arquivo não encontrado em: {csv_path}")
            print("Por favor, coloque o arquivo 'cybersecurity_attacks.csv' na pasta 'data'")
            return None

        print(f"Extraindo dados de: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"Dados extraídos com sucesso! Total de registros: {len(df)}")
        return df

    except Exception as e:
        print(f"Erro ao extrair dados: {str(e)}")
        return None

def transform_data(df):
    if df is None:
        return None

    try:
        print("Iniciando transformação dos dados...")

        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        attack_types = {attack: idx+1 for idx, attack in enumerate(df['Attack Type'].unique())}
        severities = {severity: idx+1 for idx, severity in enumerate(df['Severity Level'].unique())}
        ports = {port: idx+1 for idx, port in enumerate(df['Destination Port'].unique())}

        dim_attack_type = pd.DataFrame({
            'attack_type_id': list(attack_types.values()),
            'attack_type': list(attack_types.keys())
        })

        dim_severity = pd.DataFrame({
            'severity_id': list(severities.values()),
            'severity': list(severities.keys())
        })

        dim_destination_port = pd.DataFrame({
            'port_id': list(ports.values()),
            'destination_port': list(ports.keys())
        })

        timestamps = df['Timestamp'].unique()
        dim_timestamp = pd.DataFrame({
            'timestamp': timestamps,
            'year': [ts.year for ts in timestamps],
            'month': [ts.month for ts in timestamps],
            'day': [ts.day for ts in timestamps],
            'hour': [ts.hour for ts in timestamps]
        })

        print("Transformação dos dados concluída!")
        return {
            'dim_attack_type': dim_attack_type,
            'dim_severity': dim_severity,
            'dim_destination_port': dim_destination_port,
            'dim_timestamp': dim_timestamp
        }

    except Exception as e:
        print(f"Erro ao transformar dados: {str(e)}")
        return None

def load_data(transformed_data):
    if transformed_data is None:
        return

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

        for table_name, df in transformed_data.items():
            print(f"Carregando dados na tabela {table_name}...")
            df.to_sql(table_name, engine, if_exists="replace", index=False)
            print(f"Dados carregados com sucesso na tabela {table_name}!")

    except Exception as e:
        print(f"Erro ao carregar dados: {str(e)}")

def run_etl():
    print("Iniciando pipeline ETL...")

    df = extract_data()
    if df is None:
        return

    transformed_data = transform_data(df)
    if transformed_data is None:
        return

    load_data(transformed_data)

    print("Pipeline ETL concluído com sucesso!")

if __name__ == "__main__":
    run_etl()