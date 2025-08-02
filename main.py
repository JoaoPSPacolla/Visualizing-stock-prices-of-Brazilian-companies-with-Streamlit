#importando bibliotecas
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta

#criar funções de carregamento de dados
@st.cache_data #armazena a função na memória cache, o que faz carregar os dados mais rapidamente
def carregar_dados(empresas):
    cotacoes_acao = yf.download(empresas, start="2010-01-01", end="2025-07-01")["Close"] #chama os dados (as empresas), seta um data especifica , pega especificamente a coluna [close] do yahoo
    return cotacoes_acao

@st.cache_data 
def carregar_tickers_acoes():
    base_tickers = pd.read_csv("acoes.csv")
    tickers = list(base_tickers["Ticker"])
    tickers = [item + ".SA" for item in tickers] #list comprehension - adicionando o .SA ao final de cada ticker de ação
#nova_lista = []
#for item in tickers:
#    nova_lista.append(item + ".SA")
#tickers = nova_lista 
# Poderia escrever aquele list comprehension dessa maneira como está cima também.
    return tickers

acoes = carregar_tickers_acoes()
dados = carregar_dados(acoes) # O python consegue automaticamente entender o que é uma lista, por isso não precisa criar um for aqui para percorrer todos os valores , mas apenas passar o nome da lista

#preparar as visualizações = filtros
st.sidebar.header("Filtros")

#filtro de ações
#lista_acoes = st.multiselect("Escolha as ações para visualizar", dados.columns) 
lista_acoes = st.sidebar.multiselect("Escolha as ações para visualizar", dados.columns) #Para colocar itens dentro da sidebar, basta simplesmente inserir o .sidebar depois do st
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: "Close"})

#filtro de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider("Selecione o período", 
                  min_value=data_inicial, #onde começa
                  max_value=data_final, #onde termina
                  value=(data_inicial, data_final), #onde voce está selecionando
                  step=timedelta(days=1)) #aqui você controla de quantos em quantos dias a sidebar vai alterando. O padrão é 1, então não precisa colocar, mas fica aí para lembrar

dados = dados.loc[intervalo_data[0]:intervalo_data[1]]

#criar gráfico

st.write(f'''
# Histórico dos ativos
''')
st.line_chart(dados) # X = DATA ; Y = CLOSE

#calculo de performance
texto_performance_ativos = ""
texto_performance_carteira = ""

if len(lista_acoes) == 0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes) == 1:
    dados = dados.rename(columns={"Close": acao_unica})

carteira =[1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)

for i, acao in enumerate(lista_acoes):
    performance_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] -1
    performance_ativo = float(performance_ativo)

    carteira[i] = carteira[i] * (1 + performance_ativo)

    if performance_ativo > 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}:  :green[{performance_ativo:.1%}]"
    elif performance_ativo < 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}:  :red[{performance_ativo:.1%}]"
    else:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: {performance_ativo:.1%}"

total_final_carteira = sum(carteira)
performance_carteira = total_final_carteira / total_inicial_carteira - 1

if performance_carteira > 0:
    texto_performance_carteira = f"Performance da carteira com todos os ativos:  :green[{performance_carteira:.1%}]"
elif performance_carteira < 0:
    texto_performance_carteira = f"Performance da carteira com todos os ativos:  :red[{performance_carteira:.1%}]"
else:
    texto_performance_carteira = f"Performance da carteira com todos os ativos:  {performance_carteira:.1%}"


st.write(f'''
### Performance dos Ativos
Essa foi a performance de cada ativo no período selecionado:

{texto_performance_ativos}         

{texto_performance_carteira}
''') # linguagem markdown

