import streamlit as st
from streamlit_echarts import st_echarts
from pathlib import Path
import pandas as pd

def CriarOpcoesGrafico(titulo, nome, data, tipoGrafico):
    """Cria o dicionário de opções para um gráfico ECharts."""
    options = {}
    if tipoGrafico == 'Donut':
        options = {
            "title": {"text": titulo, "left": "center"},
            "tooltip": {"trigger": "item", "formatter": "<b>{a} <br/>{b}: {c} ({d}%)</b>"},
            "legend": {"top": "10%", "left": "center", "orient": "vertical"},
            "series": [{
                "name": nome,
                "type": "pie",
                "radius": ["40%", "70%"],
                "avoidLabelOverlap": False,
                "itemStyle": {"borderRadius": 10, "borderColor": "#fff", "borderWidth": 2},
                "label": {"show": False, "position": "center"},
                "emphasis": {"label": {"show": True, "fontSize": "30", "fontWeight": "bold"}},
                "labelLine": {"show": False},
                "data": data
            }]
        }
    elif tipoGrafico == 'Linha':
        options = {
            "title": {"text": titulo, "left": "center"},
            "tooltip": {"trigger": "axis"},
            "legend": {"top": "10%", "left": "center"},
            "grid": {"top": '25%', "left": '3%', "right": '4%', "bottom": '3%', "containLabel": True},
            "xAxis": {"type": "category", "boundaryGap": False, "data": data[0]},
            "yAxis": {"type": "value", "axisLabel": {"formatter": 'R$ {value}'}},
            "series": [{"name": nome, "data": data[1], "type": "line", "smooth": True}],
        }
    elif tipoGrafico == 'Linhas':
        options = {
            "title": {"text": titulo, "left": "center"},
            "tooltip": {"trigger": "axis"},
            "legend": {"top": "10%", "left": "center", "type": "scroll"},
            "grid": {"top": '25%', "left": '3%', "right": '4%', "bottom": '3%', "containLabel": True},
            "xAxis": {"type": "category", "boundaryGap": False, "data": data['categorias']},
            "yAxis": {"type": "value"},
            "series": data['series'],
        }
    return options


def Filtragem(dataframes, filtro_faixa, filtro_sexo, filtro_raca):
    """Aplica os filtros a uma lista de dataframes e retorna a lista filtrada."""
    dfs_filtrados = []
    mapa_sexo = {"Masculino": [1], "Feminino": [2, 3]}

    for df in dataframes:
        df_temp = df.copy() 
        if filtro_faixa != "Sem Filtro":
            df_temp = df_temp[df_temp['Faixa_Etaria_Label'] == filtro_faixa]
        if filtro_sexo != "Sem Filtro":
            df_temp = df_temp[df_temp['Sexo'].isin(mapa_sexo[filtro_sexo])]
        if filtro_raca != "Sem Filtro":
            df_temp = df_temp[df_temp['Raca_Cor_Label'] == filtro_raca]
        dfs_filtrados.append(df_temp)
    return dfs_filtrados


def exibir_em_grade(opcoes_graficos, configuracoes):
    """Função auxiliar para exibir gráficos em um layout de grade."""
    if not opcoes_graficos:
        st.info("Nenhuma cidade selecionada ou dados disponíveis para este gráfico.")
        return

    max_graficos, altura = configuracoes[0], configuracoes[1]
    for i in range(0, len(opcoes_graficos), max_graficos):
        linha = opcoes_graficos[i:i + max_graficos]
        colunas = st.columns(len(linha))
        for j, (titulo, nome, dados, tipo) in enumerate(linha):
            with colunas[j]:
                st_echarts(options=CriarOpcoesGrafico(titulo, nome, dados, tipo), height=altura)

def GraficoCustoAnual(checkBoxs, bases, configuracoes, anos_selecionados):
    st.header("Custo Anual com Internações por Má Nutrição")
    
    def prepara_dados(df):
        df_ano = df[df["Ano_Competencia"].isin(anos_selecionados)] if anos_selecionados else df
        if df_ano.empty: return None
        custo = df_ano.groupby('Ano_Competencia')['Valor_Gasto'].sum().round(2)
        return [custo.index.tolist(), custo.values.tolist()]

    opcoes = []
    nomes_cidades = ["Divinópolis", "Ouro Branco", "São João Del Rei", "Sete Lagoas"]
    for i, (selecionado, base) in enumerate(zip(checkBoxs, bases)):
        if selecionado:
            dados = prepara_dados(base)
            if dados:
                opcoes.append((nomes_cidades[i], "Custo Total (R$)", dados, 'Linha'))
    
    exibir_em_grade(opcoes, configuracoes)

def GraficoFaixaEtaria(checkBoxs, bases, configuracoes):
    st.header("Distribuição de Internações por Faixa Etária")

    def prepara_dados(df):
        if df.empty: return None
        contagem = df['Faixa_Etaria_Label'].value_counts()
        return [{"value": v, "name": k} for k, v in contagem.items()]

    opcoes = []
    nomes_cidades = ["Divinópolis", "Ouro Branco", "São João Del Rei", "Sete Lagoas"]
    for i, (selecionado, base) in enumerate(zip(checkBoxs, bases)):
        if selecionado:
            dados = prepara_dados(base)
            if dados:
                opcoes.append((nomes_cidades[i], "Nº de Internações", dados, 'Donut'))

    exibir_em_grade(opcoes, configuracoes)

def GraficoRaca(checkBoxs, bases, configuracoes):
    st.header("Distribuição de Internações por Raça/Cor")

    def prepara_dados(df):
        if df.empty: return None
        contagem = df['Raca_Cor_Label'].value_counts()
        return [{"value": v, "name": k} for k, v in contagem.items()]

    opcoes = []
    nomes_cidades = ["Divinópolis", "Ouro Branco", "São João Del Rei", "Sete Lagoas"]
    for i, (selecionado, base) in enumerate(zip(checkBoxs, bases)):
        if selecionado:
            dados = prepara_dados(base)
            if dados:
                opcoes.append((nomes_cidades[i], "Nº de Internações", dados, 'Donut'))

    exibir_em_grade(opcoes, configuracoes)

def GraficoTendenciaPorFaixaEtaria(checkBoxs, bases, configuracoes, anos_selecionados):
    st.header("Tendência de Internações por Faixa Etária")

    def prepara_dados(df):
        df_ano = df[df["Ano_Competencia"].isin(anos_selecionados)] if anos_selecionados else df
        if df_ano.empty: return None
        
        contagem = df_ano.groupby(['Ano_Competencia', 'Faixa_Etaria_Label']).size().reset_index(name='contagem')
        df_pivot = contagem.pivot(index='Ano_Competencia', columns='Faixa_Etaria_Label', values='contagem').fillna(0)
        
        series = []
        for faixa in df_pivot.columns:
            series.append({"name": faixa, "data": df_pivot[faixa].tolist(), "type": "line", "smooth": True})
        
        return {"categorias": df_pivot.index.tolist(), "series": series}

    opcoes = []
    nomes_cidades = ["Divinópolis", "Ouro Branco", "São João Del Rei", "Sete Lagoas"]
    for i, (selecionado, base) in enumerate(zip(checkBoxs, bases)):
        if selecionado:
            dados = prepara_dados(base)
            if dados and dados['series']:
                opcoes.append((nomes_cidades[i], "Nº de Internações", dados, 'Linhas'))

    exibir_em_grade(opcoes, configuracoes)


@st.cache_data
def carregar_dados_iniciais():
    """Carrega e prepara os dados de todas as cidades, executado apenas uma vez."""
    diretorio_base = Path(__file__).parent / 'database'
    arquivos = {
        "Divinópolis": "dadosFiltradosDivinopolis.csv",
        "Ouro Branco": "dadosFiltradosOuroBranco.csv",
        "São João Del Rei": "testeSJDR.csv",
        "Sete Lagoas": "dadosFiltradosSeteLagoas.csv"
    }
    dataframes = []
    for cidade, arquivo in arquivos.items():
        try:
            df = pd.read_csv(diretorio_base / arquivo, sep=';')
            df['Valor_Gasto'] = df['Valor_Gasto'].astype(str).str.replace(',', '.').astype(float)
            dataframes.append(df)
        except FileNotFoundError:
            st.warning(f"Arquivo não encontrado para {cidade}. Gráficos para esta cidade não serão exibidos.")
            dataframes.append(pd.DataFrame())
    return dataframes

def main():
    st.set_page_config(page_title="Dashboard SIHSUS", page_icon="📊", layout="wide")

    bases_originais = carregar_dados_iniciais()
    
    mapa_raca = {"1": "Branca", "2": "Preta", "3": "Parda", "4": "Amarela", "5": "Indígena", "99": "Sem Informação"}
    mapa_faixas = {'A': '0-14 anos', 'B': '15-29 anos', 'C': '30-44 anos', 'D': '45-59 anos', 'E': '60+ anos'}
    
    for df in bases_originais:
        if not df.empty:
            df['Raca_Cor_Label'] = df['Raca_Cor'].astype(str).map(mapa_raca)
            df['Faixa_Etaria_Label'] = df['Faixa_Etaria'].map(mapa_faixas)

    with st.sidebar:
        st.markdown("## Filtros de Cidades")
        check_div = st.checkbox("Divinópolis", value=False)
        check_ob = st.checkbox("Ouro Branco", value=False)
        check_sjdr = st.checkbox("São João Del Rei", value=True)
        check_sl = st.checkbox("Sete Lagoas", value=False)
        
        st.markdown("---")
        st.markdown("## Configurações de Layout")
        max_graficos_linha = st.slider("Gráficos por linha", 1, 4, 4)
        altura_grafico = st.slider("Altura dos gráficos (px)", 350, 1000, 400)
        
        st.markdown("---")
        st.markdown("## Filtros de Dados")
        
        with st.expander("Ano"):
            anos_disponiveis = sorted(pd.concat(df['Ano_Competencia'] for df in bases_originais if not df.empty).unique())
            anos_selecionados = st.multiselect("Selecione o(s) Ano(s)", options=anos_disponiveis, default=anos_disponiveis)
        
        with st.expander("Faixa Etária"):
            opcoes_faixa = ['Sem Filtro'] + list(mapa_faixas.values())
            filtro_faixa = st.radio("Filtrar por faixa etária", opcoes_faixa)

        with st.expander("Sexo"):
            filtro_sexo = st.radio("Filtrar por sexo", ['Sem Filtro', 'Feminino', 'Masculino'])

        with st.expander("Raça/Cor"):
            opcoes_raca = ['Sem Filtro'] + list(mapa_raca.values())
            filtro_raca = st.radio("Filtrar por raça/cor", opcoes_raca)

    bases_filtradas = Filtragem(bases_originais, filtro_faixa, filtro_sexo, filtro_raca)
    
    checkBoxs = [check_div, check_ob, check_sjdr, check_sl]
    configuracoes = [max_graficos_linha, f"{altura_grafico}px"]

    st.markdown("<h1 style='text-align: center;'>Análise de Dados da Base SIHSUS</h1>", unsafe_allow_html=True)
    
    GraficoCustoAnual(checkBoxs, bases_filtradas, configuracoes, anos_selecionados)
    st.markdown("---")
    GraficoTendenciaPorFaixaEtaria(checkBoxs, bases_filtradas, configuracoes, anos_selecionados)
    st.markdown("---")
    GraficoFaixaEtaria(checkBoxs, bases_filtradas, configuracoes)
    st.markdown("---")
    GraficoRaca(checkBoxs, bases_filtradas, configuracoes)

if __name__ == '__main__':
    main()

