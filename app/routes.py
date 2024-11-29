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

####################################################################################################################################################################################

# calcular_estatisticas(partidas)
# Calcula estatísticas básicas sobre os jogos realizados.
# Determina o percentual de:
# Vitórias dos mandantes.
# Empates.
# Vitórias dos visitantes.
# Identifica os 5 placares mais frequentes.


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

####################################################################################################################################################################################

# gerar_grafico_barras(partidas)
# Gera um gráfico de barras mostrando a distribuição dos resultados:
# Vitórias dos mandantes.
# Vitórias dos visitantes.
# Empates.
# Usa os placares para categorizar os resultados.
# Retorna o gráfico em formato Base64, que pode ser exibido em uma página web.


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


####################################################################################################################################################################################

# gerar_grafico_pizza()
# Cria um gráfico de pizza dos 10 times com mais vitórias como mandantes.
# Filtra os jogos onde os mandantes venceram.
# Conta o número de vitórias para cada time e seleciona os 10 principais.
# Retorna o gráfico em formato Base64.

def gerar_grafico_pizza():
    # Filtrando os jogos onde o mandante venceu
    vitorias_mandantes = partidas_realizadas[partidas_realizadas['Placar_Mandante'] > partidas_realizadas['Placar_Visitante']]

    # Contando o número de vitórias para cada mandante
    vitorias_por_time = vitorias_mandantes['Mandante'].value_counts()

    # Selecionando os 10 times com mais vitórias como mandantes
    top_10_vitorias = vitorias_por_time.head(10)

    # Criando o gráfico de pizza
    plt.figure(figsize=(8, 8))
    plt.pie(
        top_10_vitorias,
        labels=top_10_vitorias.index,
        autopct='%1.1f%%',
        startangle=155,
        colors=sns.color_palette("pastel")
    )
    plt.title("Top 10 Times com Mais Vitórias como Mandantes")

    # Salvando o gráfico em memória
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return img_base64


####################################################################################################################################################################################

# gerar_classificacao_top_10()
# Filtra as rodadas da classificação oficial (1 a 38).
# Retorna os 10 primeiros times classificados, ordenados por pontos.


def gerar_classificacao_top_10():
    classificacao_2024 = classificacao[(classificacao['Rodada'] >= 1) & (classificacao['Rodada'] <= 38)]
    top_10_classificacao = classificacao_2024.sort_values(by='Pontos', ascending=False).head(10)
    return top_10_classificacao


####################################################################################################################################################################################

# gerar_classificacao()
# Obtém a classificação da última rodada registrada.
# Retorna a tabela de classificação em formato HTML para ser exibida em uma página web.

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
previcao = pd.read_csv("datasets/previcao.csv")

####################################################################################################################################################################################

# gerar_previsoes()
# Lê os dados de partidas realizadas e não realizadas.
# Converte as colunas categóricas (Mandante, Visitante, Estádio) em valores numéricos.
# Treina dois modelos RandomForestRegressor para prever os placares dos mandantes e visitantes.
# Faz previsões para partidas não realizadas.
# Decodifica os valores categóricos de volta para os nomes originais.
# Salva as previsões em um arquivo CSV.


# Gera Previsões 
def gerar_previsoes():
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


####################################################################################################################################################################################

# predict()
# Rota da API para exibir as previsões de partidas.
# Obtém as rodadas disponíveis e filtra a rodada selecionada pelo usuário.
# Renderiza a página predict.html com as partidas previstas.

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


####################################################################################################################################################################################

# dashboard()
# Rota principal da API.
# Filtra partidas não realizadas com base na rodada selecionada.
# Calcula estatísticas gerais dos jogos realizados.
# Gera gráficos de barras e pizza.
# Obtém a classificação oficial e o top 10 times.
# Renderiza a página dashboard.html com todas as informações e gráficos.


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
