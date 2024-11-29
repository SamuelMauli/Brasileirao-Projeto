import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

partidas_realizadas = "Partidas_Realizadas.csv"
partidas_nao_realizadas = "Partidas_Nao_Realizadas.csv"

dados_realizados = pd.read_csv(partidas_realizadas)
dados_nao_realizados = pd.read_csv(partidas_nao_realizadas)

# Codificando as colunas categóricas manualmente
dados_realizados['Mandante'], mandantes_unicos = pd.factorize(dados_realizados['Mandante'])
dados_realizados['Visitante'], visitantes_unicos = pd.factorize(dados_realizados['Visitante'])

# Lidando com valores inválidos nos placares
dados_realizados['Placar_Mandante'] = pd.to_numeric(dados_realizados['Placar_Mandante'], errors='coerce').fillna(0).astype(int)
dados_realizados['Placar_Visitante'] = pd.to_numeric(dados_realizados['Placar_Visitante'], errors='coerce').fillna(0).astype(int)
dados_realizados['Estadio'], estadios_unicos = pd.factorize(dados_realizados['Estadio'])

# Separando os dados em entradas (X) e saídas (y)
entradas = dados_realizados[['Rodada', 'Mandante', 'Visitante', 'Estadio']]
saidas = dados_realizados[['Placar_Mandante', 'Placar_Visitante']]

# Dividindo os dados em conjuntos de treino e teste
X_treino, X_teste, y_treino, y_teste = train_test_split(entradas, saidas, test_size=0.2, random_state=42)

# Criando e treinando os modelos
modelo_mandante = RandomForestRegressor(random_state=42)
modelo_visitante = RandomForestRegressor(random_state=42)

modelo_mandante.fit(X_treino, y_treino['Placar_Mandante'])
modelo_visitante.fit(X_treino, y_treino['Placar_Visitante'])

# Testando os modelos
predicoes_mandante = modelo_mandante.predict(X_teste)
predicoes_visitante = modelo_visitante.predict(X_teste)

# Calculando os erros médios
erro_mandante = mean_squared_error(y_teste['Placar_Mandante'], predicoes_mandante)
erro_visitante = mean_squared_error(y_teste['Placar_Visitante'], predicoes_visitante)

print("\nErro médio (mandante):", np.sqrt(erro_mandante))
print("Erro médio (visitante):", np.sqrt(erro_visitante))

# Preenchendo colunas ausentes, se necessário
if 'Estadio' not in dados_nao_realizados.columns:
    dados_nao_realizados['Estadio'] = 0

# Preparando os dados das partidas não realizadas
dados_nao_realizados['Mandante'] = pd.Categorical(dados_nao_realizados['Mandante'], categories=mandantes_unicos).codes
dados_nao_realizados['Visitante'] = pd.Categorical(dados_nao_realizados['Visitante'], categories=visitantes_unicos).codes
dados_nao_realizados['Estadio'] = pd.Categorical(dados_nao_realizados['Estadio'], categories=estadios_unicos).codes

# Selecionando as entradas das partidas não realizadas
entradas_nao_realizadas = dados_nao_realizados[['Rodada', 'Mandante', 'Visitante', 'Estadio']]

# Fazendo previsões
print("\nFazendo previsões para partidas não realizadas...")
previsao_mandante = modelo_mandante.predict(entradas_nao_realizadas)
previsao_visitante = modelo_visitante.predict(entradas_nao_realizadas)

# Adicionando as previsões no DataFrame
dados_nao_realizados['Placar_Mandante_Previsto'] = np.round(previsao_mandante).astype(int)
dados_nao_realizados['Placar_Visitante_Previsto'] = np.round(previsao_visitante).astype(int)

# Decodificando as colunas categóricas para os valores originais
print("\nDecodificando as colunas categóricas...")
dados_nao_realizados['Mandante'] = pd.Categorical.from_codes(dados_nao_realizados['Mandante'], categories=mandantes_unicos)
dados_nao_realizados['Visitante'] = pd.Categorical.from_codes(dados_nao_realizados['Visitante'], categories=visitantes_unicos)

if 'Estadio' in dados_nao_realizados.columns:
    dados_nao_realizados = dados_nao_realizados.drop(columns=['Estadio'])

# Salvando os resultados
pasta_saida = "datasets"
if not os.path.exists(pasta_saida):
    os.makedirs(pasta_saida)

arquivo_saida = os.path.join(pasta_saida, "Partidas_Previstas.csv")
dados_nao_realizados.to_csv(arquivo_saida, index=False)