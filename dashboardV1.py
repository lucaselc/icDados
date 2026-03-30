import streamlit as st
from streamlit_echarts import st_echarts
import pandas as pd
import numpy as np
import gdown
import os

def get_nome_mes(mes):
    try:
        mes_num = int(mes)
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
            7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(mes_num, str(mes))
    except:
        return str(mes)

# funções de graficos
def CriarOpcoesGrafico(titulo, nome, data, tipoGrafico):
    """Cria o dicionário de opções para um gráfico ECharts com ajustes de legenda."""
    options = {}
    if tipoGrafico == 'Donut':
        options = {
            "title": {"text": titulo, "left": "center"},
            "tooltip": {"trigger": "item", "formatter": "<b>{a} <br/>{b}: {c} ({d}%)</b>"},
            "legend": {"bottom": "0%", "left": "center", "orient": "horizontal"},
            "series": [{
                "name": nome,
                "type": "pie",
                "radius": ["40%", "70%"],
                "center": ["50%", "45%"], 
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
            "legend": {"bottom": "0%", "left": "center", "type": "scroll"},
            "grid": {"top": '15%', "left": '3%', "right": '4%', "bottom": '15%', "containLabel": True},
            "xAxis": {"type": "category", "boundaryGap": False, "data": data.get('categories', [])},
            "yAxis": {"type": "value", "axisLabel": {"formatter": 'R$ {value}'} if 'Custo' in titulo or 'Gasto' in titulo else {}},
            "series": data.get('series', [])
        }
    elif tipoGrafico == 'LinhaDupla':
        options = {
            "title": {"text": titulo, "left": "center"},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
            "legend": {"bottom": "0%", "left": "center"},
            "grid": {"top": '20%', "left": '3%', "right": '4%', "bottom": '15%', "containLabel": True},
            "xAxis": [{"type": "category", "data": data['categories']}],
            "yAxis": [
                {"type": "value", "name": data['y_axis_name_left'], "position": "left", "axisLabel": {"formatter": '{value} %'}},
                {"type": "value", "name": data['y_axis_name_right'], "position": "right", "axisLabel": {"formatter": 'R$ {value}'}}
            ],
            "series": [
                {"name": data['series_name_left'], "type": "line", "yAxisIndex": 0, "data": data['series_data_left'], "smooth": True},
                {"name": data['series_name_right'], "type": "line", "yAxisIndex": 1, "data": data['series_data_right'], "smooth": True}
            ]
        }
    return options

# funções do sihsus
def Filtragem(dataframes, filtro_faixa, filtro_sexo, filtro_raca):
    """Aplica os filtros a uma lista de dataframes e retorna a lista filtrada."""
    dfs_filtrados = []
    mapa_sexo = {"Masculino": [1], "Feminino": [2, 3]}

    for df in dataframes:
        df_temp = df.copy() 
        if not df_temp.empty:
            if filtro_faixa != "Sem Filtro":
                df_temp = df_temp[df_temp['Faixa_Etaria_Label'] == filtro_faixa]
            if filtro_sexo != "Sem Filtro":
                df_temp = df_temp[df_temp['Sexo'].isin(mapa_sexo[filtro_sexo])]
            if filtro_raca != "Sem Filtro":
                df_temp = df_temp[df_temp['Raca_Cor_Label'] == filtro_raca]
        dfs_filtrados.append(df_temp)
    return dfs_filtrados

def exibir_em_grade(opcoes_graficos, configuracoes):
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
    st.header("Custo anual com internações relacionadas aos CIDs-alvo")
    
    def prepara_dados(df):
        df_ano = df[df["Ano_Competencia"].isin(anos_selecionados)] if anos_selecionados else df
        if df_ano.empty: return None
        custo = df_ano.groupby('Ano_Competencia')['Valor_Gasto'].sum().round(2)
        return {
            "categories": custo.index.tolist(),
            "series": [{"name": "Custo Total (R$)", "data": custo.values.tolist(), "type": "line", "smooth": True}]
        }

    opcoes = []
    nomes_cidades = ["Divinópolis", "Ouro Branco", "São João Del Rei", "Sete Lagoas"]
    for i, (selecionado, base) in enumerate(zip(checkBoxs, bases)):
        if selecionado and not base.empty:
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
        if selecionado and not base.empty:
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
        if selecionado and not base.empty:
            dados = prepara_dados(base)
            if dados:
                opcoes.append((nomes_cidades[i], "Nº de Internações", dados, 'Donut'))

    exibir_em_grade(opcoes, configuracoes)

def GraficoTendenciaPorFaixaEtaria(checkBoxs, bases, configuracoes, anos_selecionados):
    st.header("Tendência de Internações por Faixa Etária (Anual)")

    def prepara_dados(df):
        df_ano = df[df["Ano_Competencia"].isin(anos_selecionados)] if anos_selecionados else df
        if df_ano.empty: return None
        
        contagem = df_ano.groupby(['Ano_Competencia', 'Faixa_Etaria_Label']).size().reset_index(name='contagem')
        df_pivot = contagem.pivot(index='Ano_Competencia', columns='Faixa_Etaria_Label', values='contagem').fillna(0)
        
        series = []
        for faixa in df_pivot.columns:
            series.append({"name": faixa, "data": df_pivot[faixa].tolist(), "type": "line", "smooth": True})
        
        return {"categories": df_pivot.index.tolist(), "series": series}

    opcoes = []
    nomes_cidades = ["Divinópolis", "Ouro Branco", "São João Del Rei", "Sete Lagoas"]
    for i, (selecionado, base) in enumerate(zip(checkBoxs, bases)):
        if selecionado and not base.empty:
            dados = prepara_dados(base)
            if dados and dados['series']:
                opcoes.append((nomes_cidades[i], "Nº de Internações", dados, 'Linha'))

    exibir_em_grade(opcoes, configuracoes)

def GraficoEvolucaoMensalSIHSUS(checkBoxs, bases, ano, configuracoes):
    st.header(f"Evolução Mensal do Custo - {ano}")
    
    opcoes = []
    nomes_cidades = ["Divinópolis", "Ouro Branco", "São João Del Rei", "Sete Lagoas"]
    
    for i, (selecionado, base) in enumerate(zip(checkBoxs, bases)):
        if selecionado and not base.empty:
            if 'Mes_Competencia' not in base.columns:
                st.warning(f"Base de {nomes_cidades[i]} não possui a coluna 'Mes_Competencia'. Verifique os dados.")
                continue

            df_ano = base[base['Ano_Competencia'] == ano]
            if df_ano.empty:
                continue
            
            contagem = df_ano.groupby('Mes_Competencia')['Valor_Gasto'].sum().round(2)
            
            try:
                contagem.index = contagem.index.astype(int)
                contagem = contagem.sort_index()
            except:
                pass 

            meses_labels = [get_nome_mes(m) for m in contagem.index]
            valores = contagem.values.tolist()
            
            dados = {
                "categories": meses_labels,
                "series": [{"name": "Valor Gasto (R$)", "data": valores, "type": "line", "smooth": True}]
            }
            
            opcoes.append((nomes_cidades[i], "Custo Total (R$)", dados, 'Linha'))
    
    exibir_em_grade(opcoes, configuracoes)



@st.cache_data
def preparar_dados_drive():
    """Baixa toda a pasta de bases de dados do Google Drive caso os arquivos não existam localmente."""
    pasta_destino = "database"
    os.makedirs(pasta_destino, exist_ok=True)
    
    caminho_sisvan = f"{pasta_destino}/sisvanSjdr.csv"
    
    if not os.path.exists(caminho_sisvan):
        url_pasta = 'https://drive.google.com/drive/folders/1eSsElYf0QYCCVaird5R5vSzxBsMC1RNu?usp=sharing'
        gdown.download_folder(url_pasta, output=pasta_destino, quiet=False, use_cookies=False)

@st.cache_data
def carregar_dados_sihsus():
    arquivos = {
        "Divinópolis": "database/dadosFiltradosDivinopolis.csv",
        "Ouro Branco": "database/dadosFiltradosOuroBranco.csv",
        "São João Del Rei": "database/dadosFiltradosSaoJoaoDelRei.csv",
        "Sete Lagoas": "database/dadosFiltradosSeteLagoas.csv"
    }
    
    dataframes = {}
    for cidade, caminho in arquivos.items():
        if os.path.exists(caminho):
            df = pd.read_csv(caminho, sep=';')
            if 'Valor_Gasto' in df.columns and df['Valor_Gasto'].dtype == 'object':
                df['Valor_Gasto'] = df['Valor_Gasto'].astype(str).str.replace(',', '.').astype(float)
            dataframes[cidade] = df
        else:
            dataframes[cidade] = pd.DataFrame()
            
    return dataframes


@st.cache_data
def carregar_dados_sisvan():
    caminho = "database/sisvanSjdr.csv"
    
    if not os.path.exists(caminho):
        st.error(f"Arquivo '{caminho}' não encontrado.")
        return pd.DataFrame()

    df = pd.read_csv(caminho, sep=';', encoding='iso-8859-1')

    df['ANO_COMPETENCIA'] = df['NU_COMPETENCIA'].astype(str).str[:4].astype(int)
    df['MES_COMPETENCIA'] = df['NU_COMPETENCIA'].astype(str).str[4:].astype(int)

    cols_nutri = ['CO_ESTADO_NUTRI_ADULTO', 'CO_ESTADO_NUTRI_IDOSO', 'CRI. IMC X IDADE', 'ADO. IMC X IDADE', 'CO_ESTADO_NUTRI_IMC_SEMGEST']
    
    df['ESTADO_NUTRICIONAL'] = df[cols_nutri[0]]
    for col in cols_nutri[1:]:
        if col in df.columns:
            df['ESTADO_NUTRICIONAL'] = df['ESTADO_NUTRICIONAL'].fillna(df[col])
            
    mapa_nutri = {
        'Adequado ou eutrófico': 'Eutrofia',
        'Eutrofia': 'Eutrofia',
        'Peso adequado para idade': 'Eutrofia',
        'Sobrepeso': 'Sobrepeso',
        'Risco de sobrepeso': 'Risco de Sobrepeso',
        'Obesidade': 'Obesidade',
        'Obesidade Grau I': 'Obesidade',
        'Obesidade Grau II': 'Obesidade',
        'Obesidade Grau III': 'Obesidade',
        'Baixo peso': 'Baixo Peso',
        'Magreza': 'Baixo Peso',
        'Magreza acentuada': 'Baixo Peso'
    }
    
    df['ESTADO_NUTRICIONAL_LABEL'] = df['ESTADO_NUTRICIONAL'].map(mapa_nutri).fillna('Não Informado/Outros')
    df = df[df['ESTADO_NUTRICIONAL_LABEL'] != 'Não Informado/Outros']
    
    return df


def GraficoEvolucaoNutricional(df, configuracoes):
    st.header("Evolução Temporal Anual (Geral)")
    
    if df.empty:
        st.info("Sem dados para exibir.")
        return

    dados = df.groupby(['ANO_COMPETENCIA', 'ESTADO_NUTRICIONAL_LABEL']).size().reset_index(name='contagem')
    pivot_dados = dados.pivot(index='ANO_COMPETENCIA', columns='ESTADO_NUTRICIONAL_LABEL', values='contagem').fillna(0)
    
    series = []
    for estado in pivot_dados.columns:
        series.append({
            "name": estado,
            "data": pivot_dados[estado].tolist(),
            "type": "line",
            "smooth": True
        })
    
    opcoes = {
        "categories": pivot_dados.index.astype(str).tolist(),
        "series": series
    }
    
    st_echarts(options=CriarOpcoesGrafico("Evolução Anual por Estado Nutricional", "Pessoas", opcoes, 'Linha'), height=configuracoes[1])

def GraficoEvolucaoMensalSISVAN(df, ano, configuracoes):
    st.header(f"Evolução Mensal do Estado Nutricional - {ano}")
    
    df_ano = df[df['ANO_COMPETENCIA'] == ano]
    if df_ano.empty:
        st.info(f"Sem dados mensais para o ano {ano}.")
        return

    dados = df_ano.groupby(['MES_COMPETENCIA', 'ESTADO_NUTRICIONAL_LABEL']).size().reset_index(name='contagem')
    pivot_dados = dados.pivot(index='MES_COMPETENCIA', columns='ESTADO_NUTRICIONAL_LABEL', values='contagem').fillna(0)
    
    pivot_dados = pivot_dados.sort_index()
    
    series = []
    for estado in pivot_dados.columns:
        series.append({
            "name": estado,
            "data": pivot_dados[estado].tolist(),
            "type": "line",
            "smooth": True
        })
    
    meses_labels = [get_nome_mes(m) for m in pivot_dados.index]
    
    opcoes = {
        "categories": meses_labels,
        "series": series
    }
    
    st_echarts(options=CriarOpcoesGrafico(f"Evolução Mensal ({ano})", "Pessoas", opcoes, 'Linha'), height=configuracoes[1])

def GraficoDistribuicaoNutricional(df, ano, configuracoes):
    st.header(f"Distribuição do Estado Nutricional - {ano}")
    
    df_ano = df[df['ANO_COMPETENCIA'] == ano]
    
    if df_ano.empty:
        st.info(f"Sem dados para o ano {ano}.")
        return

    contagem = df_ano['ESTADO_NUTRICIONAL_LABEL'].value_counts()
    dados_donut = [{"value": int(v), "name": k} for k, v in contagem.items()]
    
    st_echarts(options=CriarOpcoesGrafico("Distribuição (%)", "Pessoas", dados_donut, 'Donut'), height=configuracoes[1])


def main():
    st.set_page_config(page_title="Dashboard Dados Sociais", page_icon="📊", layout="wide")

    preparar_dados_drive()

    base_selecionada = st.sidebar.selectbox("Selecione a Base de Dados", ["SIHSUS", "SISVAN"])

    bases_dict_sihsus = carregar_dados_sihsus()
    bases_sihsus_list = list(bases_dict_sihsus.values())

    if base_selecionada == "SIHSUS":
        mapa_raca = {"1": "Branca", "2": "Preta", "3": "Parda", "4": "Amarela", "5": "Indígena", "99": "Sem Informação"}
        mapa_faixas = {'A': '0-14 anos', 'B': '15-29 anos', 'C': '30-44 anos', 'D': '45-59 anos', 'E': '60+ anos'}
        
        for df in bases_sihsus_list:
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
            st.markdown("## Layout")
            max_graficos_linha = st.slider("Gráficos por linha", 1, 4, 4)
            altura_grafico = st.slider("Altura dos gráficos (px)", 350, 1000, 400)
            
            st.markdown("---")
            st.markdown("## Filtros de Dados")
            
            anos_todos = []
            for df in bases_sihsus_list:
                if not df.empty and 'Ano_Competencia' in df.columns:
                    anos_todos.extend(df['Ano_Competencia'].unique())
            anos_disponiveis = sorted(list(set(anos_todos)))

            with st.expander("Ano (Tendência Geral)"):
                anos_selecionados = st.multiselect("Selecione Anos", options=anos_disponiveis, default=anos_disponiveis)
            
            with st.expander("Outros Filtros"):
                opcoes_faixa = ['Sem Filtro'] + list(mapa_faixas.values())
                filtro_faixa = st.radio("Faixa Etária", opcoes_faixa)
                filtro_sexo = st.radio("Sexo", ['Sem Filtro', 'Feminino', 'Masculino'])
                opcoes_raca = ['Sem Filtro'] + list(mapa_raca.values())
                filtro_raca = st.radio("Raça/Cor", opcoes_raca)

            st.markdown("---")
            st.markdown("## Análise Mensal")
            if anos_disponiveis:
                ano_mensal_sihsus = st.selectbox("Selecione o Ano para Análise Mensal", options=anos_disponiveis, index=len(anos_disponiveis)-1)
            else:
                ano_mensal_sihsus = None

        bases_filtradas = Filtragem(bases_sihsus_list, filtro_faixa, filtro_sexo, filtro_raca)
        checkBoxs = [check_div, check_ob, check_sjdr, check_sl]
        configuracoes = [max_graficos_linha, f"{altura_grafico}px"]

        st.markdown("<h1 style='text-align: center;'>Análise de Dados da Base SIHSUS</h1>", unsafe_allow_html=True)
        
        GraficoCustoAnual(checkBoxs, bases_filtradas, configuracoes, anos_selecionados)
        st.markdown("---")
        GraficoTendenciaPorFaixaEtaria(checkBoxs, bases_filtradas, configuracoes, anos_selecionados)
        st.markdown("---")
        
        if ano_mensal_sihsus:
             GraficoEvolucaoMensalSIHSUS(checkBoxs, bases_filtradas, ano_mensal_sihsus, configuracoes)
             st.markdown("---")

        GraficoFaixaEtaria(checkBoxs, bases_filtradas, configuracoes)
        st.markdown("---")
        GraficoRaca(checkBoxs, bases_filtradas, configuracoes)

    elif base_selecionada == "SISVAN":
        df_sisvan = carregar_dados_sisvan()
        
        if df_sisvan.empty:
            st.warning("Não foi possível carregar a base de dados do SISVAN.")
        else:
            with st.sidebar:
                st.markdown("## Configurações do SISVAN")
                st.info("Base Filtrada: São João del Rei")
                
                altura_grafico = st.slider("Altura dos gráficos (px)", 350, 1000, 400)
                configuracoes = [1, f"{altura_grafico}px"]

                st.markdown("---")
                st.markdown("## Filtros")
                
                fases_vida = sorted(df_sisvan['DS_FASE_VIDA'].unique().astype(str))
                filtro_fase = st.multiselect("Fase da Vida (Geral)", options=fases_vida, default=fases_vida)

                st.markdown("---")
                st.markdown("## Análise Mensal")
                
                anos_comp = sorted(df_sisvan['ANO_COMPETENCIA'].unique())
                if anos_comp:
                    ano_detalhado = st.selectbox("Selecione o Ano", options=anos_comp, index=len(anos_comp)-1)
                else:
                    ano_detalhado = None

            df_filtrado = df_sisvan.copy()
            if filtro_fase:
                df_filtrado = df_filtrado[df_filtrado['DS_FASE_VIDA'].isin(filtro_fase)]

            st.markdown("<h1 style='text-align: center;'>Análise de Dados do SISVAN - Estado Nutricional</h1>", unsafe_allow_html=True)
            
            GraficoEvolucaoNutricional(df_filtrado, configuracoes)
            st.markdown("---")
            
            if ano_detalhado:
                GraficoEvolucaoMensalSISVAN(df_filtrado, ano_detalhado, configuracoes)
                st.markdown("---")
                GraficoDistribuicaoNutricional(df_filtrado, ano_detalhado, configuracoes)

if __name__ == '__main__':
    main()