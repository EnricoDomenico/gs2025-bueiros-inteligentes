# train_model.py
import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier # Exemplo de modelo
from sklearn.metrics import classification_report
import joblib # Para salvar o modelo

DATABASE_FILE = 'bueiros_data.db'
MODEL_FILE = 'modelo_bueiros.pkl'

def carregar_dados():
    conn = sqlite3.connect(DATABASE_FILE)
    # Selecionar dados relevantes, excluindo aqueles sem 'espaco_livre_percent'
    query = """
        SELECT 
            l.dispositivo_mac,
            l.timestamp,
            l.espaco_livre_percent,
            l.bateria_percent,
            l.status_reportado  -- Usado para criar o target ou como feature
            -- Adicionar outras features da tabela 'dispositivos' se necessário, usando JOIN
        FROM leituras l
        WHERE l.espaco_livre_percent IS NOT NULL 
        ORDER BY l.dispositivo_mac, l.timestamp
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def engenharia_de_features(df):
    print("Iniciando engenharia de features...")
    # Ordenar para cálculos baseados em tempo
    df = df.sort_values(by=['dispositivo_mac', 'timestamp'])

    # Taxa de variação do espaço livre (delta em relação à leitura anterior)
    df['delta_espaco_livre'] = df.groupby('dispositivo_mac')['espaco_livre_percent'].diff().fillna(0)
    
    # Média móvel do espaço livre nas últimas N leituras
    N = 3 # Ajustável
    df['media_movel_espaco_livre'] = df.groupby('dispositivo_mac')['espaco_livre_percent'].rolling(window=N, min_periods=1).mean().reset_index(level=0, drop=True)
    
    # Tempo desde a última leitura (em horas) - pode indicar se um sensor está offline
    # df['tempo_desde_ultima_leitura_h'] = df.groupby('dispositivo_mac')['timestamp'].diff().dt.total_seconds().fillna(0) / 3600
    
    # Features Categóricas (se houver, como 'localizacao_tipo' se você adicionar)
    # df = pd.get_dummies(df, columns=['localizacao_tipo'], dummy_na=False)

    # Para este exemplo, vamos prever se o status será 'CRITICO' na próxima leitura
    # Criando a variável alvo (target):
    # Se a *próxima* leitura para o mesmo dispositivo for 'CRITICO', então o alvo é 1, senão 0.
    df['target_sera_critico'] = df.groupby('dispositivo_mac')['status_reportado'].shift(-1) == 'CRITICO'
    df['target_sera_critico'] = df['target_sera_critico'].fillna(False).astype(int) # Preenche NaNs (última leitura) e converte para int

    # Remover linhas onde o target não pode ser determinado (a última de cada grupo)
    df = df.dropna(subset=['media_movel_espaco_livre']) # Remove NaNs de rolling window
    df = df[df.groupby('dispositivo_mac')['timestamp'].transform('count') > 1] # Garante que há uma "próxima" leitura
    
    print(f"Shape do DF após engenharia de features: {df.shape}")
    print(f"Distribuição do target:\n{df['target_sera_critico'].value_counts(normalize=True)}")
    
    return df.dropna(subset=['target_sera_critico']) # Remove a última leitura de cada grupo que não tem target


def treinar_modelo():
    df = carregar_dados()
    if df.empty or len(df) < 10: # Checagem básica
        print("Dados insuficientes para treinamento.")
        return

    df_featured = engenharia_de_features(df)
    
    if df_featured.empty or 'target_sera_critico' not in df_featured.columns or df_featured['target_sera_critico'].nunique() < 2 :
        print("Não foi possível criar features ou o target tem apenas uma classe. Verifique os dados e a lógica da engenharia de features.")
        print(df_featured.head())
        return

    # Selecionar features para o modelo
    features = ['espaco_livre_percent', 'bateria_percent', 'delta_espaco_livre', 'media_movel_espaco_livre']
    # Garantir que todas as features existem no dataframe
    features = [f for f in features if f in df_featured.columns]
    if not features:
        print("Nenhuma feature selecionada ou disponível.")
        return

    X = df_featured[features]
    y = df_featured['target_sera_critico']

    if X.empty or y.empty:
        print("Features (X) ou target (y) estão vazios após seleção.")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y if y.nunique() > 1 else None)

    print(f"Tamanho do treino: {X_train.shape}, Teste: {X_test.shape}")

    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced') # class_weight para dados desbalanceados
    model.fit(X_train, y_train)

    # Avaliar
    y_pred = model.predict(X_test)
    print("\nRelatório de Classificação no Conjunto de Teste:")
    print(classification_report(y_test, y_pred))

    # Salvar o modelo treinado
    joblib.dump(model, MODEL_FILE)
    print(f"Modelo salvo em {MODEL_FILE}")

if __name__ == '__main__':
    treinar_modelo()