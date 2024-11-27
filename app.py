import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from collections import Counter

# Carregando os datasets
partidas_realizadas = pd.read_csv("uploads/Partidas_Realizadas.csv")
partidas_nao_realizadas = pd.read_csv("uploads/Partidas_Nao_Realizadas.csv")
classificacao = pd.read_csv("uploads/Classificacao.csv")

# Convertendo datas para o formato datetime
partidas_realizadas['Data'] = pd.to_datetime(partidas_realizadas['Data'], format='%d/%m')
partidas_nao_realizadas['Data'] = pd.to_datetime(partidas_nao_realizadas['Data'], format='%d/%m')


# Função para calcular estatísticas históricas
def calcular_estatisticas(partidas):
    print("=== Estatísticas Gerais ===")
    # Taxa de vitórias dos mandantes
    vitorias_mandantes = partidas[partidas['Placar_Mandante'] > partidas['Placar_Visitante']].shape[0]
    empates = partidas[partidas['Placar_Mandante'] == partidas['Placar_Visitante']].shape[0]
    vitorias_visitantes = partidas[partidas['Placar_Mandante'] < partidas['Placar_Visitante']].shape[0]
    total_partidas = partidas.shape[0]

    print(f"Taxa de vitórias dos mandantes: {vitorias_mandantes / total_partidas * 100:.2f}%")
    print(f"Taxa de empates: {empates / total_partidas * 100:.2f}%")
    print(f"Taxa de vitórias dos visitantes: {vitorias_visitantes / total_partidas * 100:.2f}%")

    # Tendências de placares mais frequentes
    placares = partidas.apply(lambda row: f"{row['Placar_Mandante']}x{row['Placar_Visitante']}", axis=1)
    placares_freq = Counter(placares).most_common(5)
    print("\nPlacar mais frequentes:")
    for placar, freq in placares_freq:
        print(f"{placar}: {freq} vezes")


# Visualização de gráficos
def gerar_graficos(partidas):
    print("\nGerando gráficos...")

    # Gráfico de barras: Quantidade de vitórias, empates e derrotas
    resultados = partidas.copy()
    resultados['Resultado'] = resultados.apply(
        lambda row: 'Mandante' if row['Placar_Mandante'] > row['Placar_Visitante']
        else ('Visitante' if row['Placar_Mandante'] < row['Placar_Visitante'] else 'Empate'), axis=1
    )
    sns.countplot(data=resultados, x='Resultado', palette='viridis')
    plt.title("Distribuição de Resultados")
    plt.xlabel("Resultado")
    plt.ylabel("Quantidade")
    plt.show()

    # Gráfico de pizza: Distribuição de resultados
    resultados_freq = resultados['Resultado'].value_counts()
    resultados_freq.plot.pie(autopct='%1.1f%%', startangle=90, cmap='viridis')
    plt.title("Distribuição de Resultados (%)")
    plt.ylabel("")
    plt.show()

    # Gráfico de linha: Pontuação acumulada ao longo das rodadas
    plt.figure(figsize=(12, 6))
    for time in classificacao['Time'].unique():
        pontos = classificacao[classificacao['Time'] == time].sort_values('Rodada')['Pontos']
        rodadas = classificacao[classificacao['Time'] == time].sort_values('Rodada')['Rodada']
        plt.plot(rodadas, pontos, label=time)
    plt.title("Pontuação Acumulada por Rodada")
    plt.xlabel("Rodada")
    plt.ylabel("Pontos")
    plt.legend()
    plt.show()


# Comparação de desempenhos
# Comparação de desempenho detalhada
def comparar_desempenho(partidas):
    print("\n=== Desempenho em Casa vs Fora ===")

    # Frequência de gols marcados em casa e fora por partida
    gols_casa = partidas['Placar_Mandante'].value_counts().sort_index()
    gols_fora = partidas['Placar_Visitante'].value_counts().sort_index()

    # Criando um DataFrame para visualização
    desempenho = pd.DataFrame({
        'Gols por Jogo': gols_casa.index.union(gols_fora.index, sort=False),
        'Em Casa': gols_casa.reindex(gols_casa.index.union(gols_fora.index, sort=False), fill_value=0),
        'Fora de Casa': gols_fora.reindex(gols_casa.index.union(gols_fora.index, sort=False), fill_value=0)
    }).set_index('Gols por Jogo')

    # Gráfico de barras comparativo
    desempenho.plot(kind='bar', figsize=(10, 6), color=['#1f77b4', '#ff7f0e'])
    plt.title('Distribuição de Gols por Jogo: Casa vs Fora')
    plt.xlabel('Gols por Jogo')
    plt.ylabel('Quantidade de Partidas')
    plt.xticks(rotation=0)
    plt.legend(title='Local', loc='upper right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


# Previsões futuras (placeholder para integrar modelos de Machine Learning)
def previsoes_futuras(partidas_nao_realizadas, classificacao):
    print("\n=== Previsões Finais ===")
    print("Este módulo pode ser expandido para incluir algoritmos de Machine Learning, como:")
    print(" - Regressão Logística para prever resultados.")
    print(" - Árvores de Decisão para prever placares específicos.")
    print("\nDatas das partidas ainda a serem realizadas:")
    print(partidas_nao_realizadas[['Rodada', 'Mandante', 'Visitante', 'Data']])


# Execução das análises
calcular_estatisticas(partidas_realizadas)
gerar_graficos(partidas_realizadas)
comparar_desempenho(partidas_realizadas)
previsoes_futuras(partidas_nao_realizadas, classificacao)
