import pandas as pd
from pathlib import Path

def load_local_dataset():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    try:
        csv_path = data_dir / "cybersecurity_attacks.csv"
        if not csv_path.exists():
            print(f"Arquivo não encontrado em: {csv_path}")
            print("Por favor, coloque o arquivo 'cybersecurity_attacks.csv' na pasta 'data'")
            return None

        print(f"Carregando dataset de: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"Dataset carregado com sucesso! Total de registros: {len(df)}")

        return csv_path

    except Exception as e:
        print(f"Erro ao carregar o dataset: {str(e)}")
        return None

if __name__ == "__main__":
    load_local_dataset() 