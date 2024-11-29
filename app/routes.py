from flask import render_template, request
from app import app
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from collections import Counter

partidas_realizadas = pd.read_csv("datasets/Partidas_Realizadas.csv")
partidas_nao_realizadas = pd.read_csv("datasets/Partidas_Nao_Realizadas.csv")
classificacao = pd.read_csv("datasets/Classificacao.csv")
previcao = pd.read_csv("datasets/previcao.csv")  # Carregando o arquivo de previsões



def calcular_estatisticas(partidas):
    estatisticas = {}
    vitorias_mandantes = partidas[partidas['Placar_Mandante'] > partidas['Placar_Visitante']].shape[0]
    empates = partidas[partidas['Placar_Mandante'] == partidas['Placar_Visitante']].shape[0]
    vitorias_visitantes = partidas[partidas['Placar_Mandante'] < partidas['Placar_Visitante']].shape[0]
    total_partidas = partidas.shape[0]

    estatisticas['vitorias_mandantes'] = vitorias_mandantes / total_partidas * 100
    estatisticas['empates'] = empates / total_partidas * 100
    estatisticas['vitorias_visitantes'] = vitorias_visitantes / total_partidas * 100

    placares = partidas.apply(lambda row: f"{row['Placar_Mandante']}x{row['Placar_Visitante']}", axis=1)
    placares_freq = Counter(placares).most_common(5)
    estatisticas['placares_freq'] = placares_freq

    return estatisticas


def gerar_grafico_barras(partidas):
    resultados = partidas.copy()
    resultados['Resultado'] = resultados.apply(
        lambda row: 'Mandante' if row['Placar_Mandante'] > row['Placar_Visitante']
        else ('Visitante' if row['Placar_Mandante'] < row['Placar_Visitante'] else 'Empate'), axis=1
    )
    plt.figure(figsize=(8, 6))

    # Ajuste para o aviso de depreciação
    sns.countplot(data=resultados, x='Resultado', hue='Resultado', palette='viridis', legend=False)

    plt.title("Distribuição de Resultados")
    plt.xlabel("Resultado")
    plt.ylabel("Quantidade")

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return img_base64

def gerar_grafico_pizza():
    # Agrupando os dados por time e somando o número de vitórias
    vitorias_por_time = classificacao.groupby('Time')['Vitorias'].sum()

    # Selecionando os 10 times com mais vitórias
    top_10_vitorias = vitorias_por_time.sort_values(ascending=False).head(10)

    # Criando o gráfico de pizza
    plt.figure(figsize=(8, 8))
    plt.pie(top_10_vitorias, labels=top_10_vitorias.index, autopct='%1.1f%%', startangle=155,
            colors=sns.color_palette("pastel"))
    plt.title("Top 10 Times com Mais Vitórias")

    # Salvar o gráfico em memória
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return img_base64




def gerar_classificacao_top_10():
    classificacao_2024 = classificacao[(classificacao['Rodada'] >= 1) & (classificacao['Rodada'] <= 38)]
    top_10_classificacao = classificacao_2024.sort_values(by='Pontos', ascending=False).head(10)
    return top_10_classificacao


def gerar_classificacao():
    ultima_rodada = classificacao['Rodada'].max()
    ultima_rodada_classificacao = classificacao[classificacao['Rodada'] == ultima_rodada]
    classificacao_html = ultima_rodada_classificacao.sort_values(by='Posicao')[
        ['Posicao', 'Time', 'Pontos', 'Vitorias', 'Empates', 'Derrotas', 'GP', 'GC', 'SG']]
    return classificacao_html.to_html(classes='table table-striped', index=False)


partidas_nao_realizadas = pd.read_csv("datasets/Partidas_Nao_Realizadas.csv")


# Carregar os datasets
partidas_realizadas = pd.read_csv("datasets/Partidas_Realizadas.csv")
partidas_nao_realizadas = pd.read_csv("datasets/Partidas_Nao_Realizadas.csv")
classificacao = pd.read_csv("datasets/Classificacao.csv")

@app.route('/predict', methods=['GET'])
def predict():
    rodadas_disponiveis = previcao['Rodada'].unique().tolist()
    selected_rodada = request.args.get('rodada', None)

    if selected_rodada:
        previsao_partidas = previcao[previcao['Rodada'] == int(selected_rodada)]
    else:
        previsao_partidas = previcao

    return render_template('predict.html', 
                           previsao_partidas=previsao_partidas,
                           rodadas=rodadas_disponiveis,
                           selected_rodada=selected_rodada)

@app.route('/', methods=['GET'])
def dashboard():
    rodadas_disponiveis = partidas_nao_realizadas['Rodada'].unique().tolist()
    selected_rodada = request.args.get('rodada', None)

    if selected_rodada:
        partidas_filtradas = partidas_nao_realizadas[partidas_nao_realizadas['Rodada'] == int(selected_rodada)]
    else:
        partidas_filtradas = partidas_nao_realizadas

    estatisticas = calcular_estatisticas(partidas_realizadas)
    img_barras = gerar_grafico_barras(partidas_realizadas)
    classificacao_html = gerar_classificacao()
    top_10_classificacao = gerar_classificacao_top_10()
    img_pizza = gerar_grafico_pizza()

    return render_template('dashboard.html', 
                           estatisticas=estatisticas, 
                           img_barras=img_barras,
                           classificacao_html=classificacao_html, 
                           partidas_nao_realizadas=partidas_filtradas,
                           rodadas=rodadas_disponiveis,
                           selected_rodada=selected_rodada,
                           top_10_classificacao=top_10_classificacao,
                           img_pizza=img_pizza)
