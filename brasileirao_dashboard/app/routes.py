from flask import render_template
from app import app
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from collections import Counter

# Carregando os datasets
partidas_realizadas = pd.read_csv("datasets/Partidas_Realizadas.csv")
partidas_nao_realizadas = pd.read_csv("datasets/Partidas_Nao_Realizadas.csv")
classificacao = pd.read_csv("datasets/Classificacao.csv")


# Funções para estatísticas e gráficos
def calcular_estatisticas(partidas):
    estatisticas = {}
    # Taxa de vitórias dos mandantes
    vitorias_mandantes = partidas[partidas['Placar_Mandante'] > partidas['Placar_Visitante']].shape[0]
    empates = partidas[partidas['Placar_Mandante'] == partidas['Placar_Visitante']].shape[0]
    vitorias_visitantes = partidas[partidas['Placar_Mandante'] < partidas['Placar_Visitante']].shape[0]
    total_partidas = partidas.shape[0]

    estatisticas['vitorias_mandantes'] = vitorias_mandantes / total_partidas * 100
    estatisticas['empates'] = empates / total_partidas * 100
    estatisticas['vitorias_visitantes'] = vitorias_visitantes / total_partidas * 100

    # Tendências de placares mais frequentes
    placares = partidas.apply(lambda row: f"{row['Placar_Mandante']}x{row['Placar_Visitante']}", axis=1)
    placares_freq = Counter(placares).most_common(5)
    estatisticas['placares_freq'] = placares_freq

    return estatisticas


def gerar_grafico_barras(partidas):
    # Gráfico de barras: Quantidade de vitórias, empates e derrotas
    resultados = partidas.copy()
    resultados['Resultado'] = resultados.apply(
        lambda row: 'Mandante' if row['Placar_Mandante'] > row['Placar_Visitante']
        else ('Visitante' if row['Placar_Mandante'] < row['Placar_Visitante'] else 'Empate'), axis=1
    )
    plt.figure(figsize=(8, 6))
    sns.countplot(data=resultados, x='Resultado', palette='viridis')
    plt.title("Distribuição de Resultados")
    plt.xlabel("Resultado")
    plt.ylabel("Quantidade")

    # Salvar a imagem em memória
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return img_base64

def gerar_classificacao_top_10():
    # Filtrando a classificação para o intervalo de 2004 a 2024
    # Se o ano for inferido por alguma coluna de data, pode ser necessário esse passo.
    # Aqui assumimos que o dataset já está filtrado para o ano desejado, caso contrário, adicione um filtro de ano.

    classificacao_2024 = classificacao[(classificacao['Rodada'] >= 1) & (classificacao['Rodada'] <= 38)]  # Exemplo para filtrar todas as rodadas de uma temporada

    # Ordenando por Pontos e pegando os top 10
    top_10_classificacao = classificacao_2024.sort_values(by='Pontos', ascending=False).head(10)

    return top_10_classificacao


def gerar_classificacao():
    # Exibe a tabela de classificação
    classificacao_html = classificacao.sort_values(by='Posicao')[
        ['Posicao', 'Time', 'Pontos', 'Vitorias', 'Empates', 'Derrotas', 'GP', 'GC', 'SG']]
    return classificacao_html.to_html(classes='table table-striped', index=False)


@app.route('/')
def index():
    estatisticas = calcular_estatisticas(partidas_realizadas)
    img_barras = gerar_grafico_barras(partidas_realizadas)
    classificacao_html = gerar_classificacao()
    top_10_classificacao = gerar_classificacao_top_10()  # Calculando o top 10

    return render_template('dashboard.html', estatisticas=estatisticas, img_barras=img_barras,
                           classificacao_html=classificacao_html, partidas_nao_realizadas=partidas_nao_realizadas,
                           top_10_classificacao=top_10_classificacao)  # Passando o top 10 para o template
