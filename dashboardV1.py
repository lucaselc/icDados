import streamlit as st
from streamlit_echarts import st_echarts
from pathlib import Path
import pandas as pd

# Função para criar os dicionários de opções para cada gráfico

def CriarOpcoesGrafico(titulo, nome, data, tipoGrafico):
    options = {}
    if tipoGrafico == 'Donut':
        options = {
            "title": {"text": titulo, "left": "center"},
            "tooltip": {"trigger": "item", "formatter": "<b>{a} <br/>{b}: {c} ({d}%)</b>"},
            "legend": {"top": "5%", "left": "center"},
            "series": [{
                "name": nome,
                "type": "pie",
                "radius": ["40%", "70%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#fff",
                    "borderWidth": 2,
                },
                "label": {"show": False, "position": "center"},
                "emphasis": {
                    "label": {"show": True, "fontSize": "40", "fontWeight": "bold"}
                },
                "labelLine": {"show": False},
                "data": data
            }]
        }
    elif tipoGrafico == 'Linha':
        options = {
            "title": {"text": titulo, "left": "center"},
            "tooltip": {"trigger": "axis"},
            "legend": {"top": "5%", "left": "center"},
            "xAxis": {"type": "category", "boundaryGap": False, "data": data[0]},
            "yAxis": {"type": "value"},
            "series": [{
                "name": nome,
                "data": data[1],
                "type": "line",
                "smooth": True
            }],
        }


    elif tipoGrafico == 'Linhas':
        options = {
            "title": {"text": titulo, "left": "center"},
            "tooltip": {"trigger": "axis"},
            "legend": {"top": "5%", "left": "center", "type": "scroll"}, 
            "xAxis": {"type": "category", "boundaryGap": False, "data": data['categorias']}, 
            "yAxis": {"type": "value"},
            "series": data['series'], 
        }
    return options


def GraficoCustoAnual(df, configuracoes, anosSelecionados):
    st.header("Custo Anual com Internações por Má Nutrição")

    if anosSelecionados:
        df = df[df["Ano_Competencia"].isin(anosSelecionados)]

    custoAnual = df.groupby('Ano_Competencia')['Valor_Gasto'].sum().round(2)
    dadosGrafico = [custoAnual.index.tolist(), custoAnual.values.tolist()]

    st_echarts(
        options=CriarOpcoesGrafico("Evolução do Custo Total", "Custo Total (R$)", dadosGrafico, 'Linha'),
        height=configuracoes[1]
    )


def GraficoFaixaEtaria(df, configuracoes):
    st.header("Distribuição de Internações por Faixa Etária")

    mapaFaixas = {
        'A': '0-14 anos',
        'B': '15-29 anos',
        'C': '30-44 anos',
        'D': '45-59 anos',
        'E': '60+ anos'
    }
    
    contagem_faixas = df['Faixa_Etaria'].value_counts()
    dadosGrafico = [{"value": v, "name": mapaFaixas.get(k, "Não especificada")} for k, v in contagem_faixas.items()]

    st_echarts(
        options=CriarOpcoesGrafico("Internações por Faixa Etária", "Nº de Internações", dadosGrafico, 'Donut'),
        height=configuracoes[1]
    )


def GraficoRaca(df, configuracoes):
    st.header("Distribuição de Internações por Raça/Cor")

    contagemRaca = df['Raca_Cor_Label'].value_counts()
    dadosGrafico = [{"value": v, "name": k} for k, v in contagemRaca.items()]

    st_echarts(
        options=CriarOpcoesGrafico("Internações por Raça/Cor", "Nº de Internações", dadosGrafico, 'Donut'),
        height=configuracoes[1]
    )

def GraficoTendenciaPorFaixaEtaria(df, configuracoes, anosSelecionados):
    st.header("Tendência de Internações por Faixa Etária ao Longo do Tempo")

    if anosSelecionados:
        df = df[df["Ano_Competencia"].isin(anosSelecionados)]

    mapaFaixas = {
        'A': '0-14 anos', 'B': '15-29 anos', 'C': '30-44 anos',
        'D': '45-59 anos', 'E': '60+ anos'
    }
    df['Faixa_Etaria_Label'] = df['Faixa_Etaria'].map(mapaFaixas)

    # Agrupa por ano e faixa etária e conta as ocorrências
    contagemAnualFaixa = df.groupby(['Ano_Competencia', 'Faixa_Etaria_Label']).size().reset_index(name='contagem')

    # Pivota a tabela
    dfPivot = contagemAnualFaixa.pivot(
        index='Ano_Competencia', 
        columns='Faixa_Etaria_Label', 
        values='contagem'
    ).fillna(0) # Preenche anos sem dados com 0

    # Coloca cada coluna no formato de dicionario
    seriesData = []
    for faixa in dfPivot.columns:
        seriesData.append({
            "name": faixa,
            "data": dfPivot[faixa].tolist(),
            "type": "line",
            "smooth": True
        })

    dadosGrafico = {
        "categorias": dfPivot.index.tolist(),
        "series": seriesData
    }

    st_echarts(
        options=CriarOpcoesGrafico("Evolução do Nº de Internações por Faixa Etária", "Nº de Internações", dadosGrafico, 'Linhas'),
        height=configuracoes[1]
    )

def main():
    diretorioAtual = Path(__file__).parent
    caminhoArquivo = diretorioAtual / 'database' / 'dadosFiltradosSJDR.csv'

    dfSihsusSJDR = pd.read_csv(caminhoArquivo, sep=';')
    dfSihsusSJDR['Valor_Gasto'] = dfSihsusSJDR['Valor_Gasto'].astype(str).str.replace(',', '.').astype(float)

    mapaSexo = {"Masculino": [1], "Feminino": [2, 3]}
    mapaRaca = {
        "1": "Branca", "2": "Preta", "3": "Parda",
        "4": "Amarela", "5": "Indígena", "99": "Sem Informação"
    }
    mapaFaixas = {
        'A': '0-14 anos', 'B': '15-29 anos', 'C': '30-44 anos',
        'D': '45-59 anos', 'E': '60+ anos'
    }

    dfSihsusSJDR['Raca_Cor_Label'] = dfSihsusSJDR['Raca_Cor'].astype(str).map(mapaRaca)
    dfSihsusSJDR['Faixa_Etaria_Label'] = dfSihsusSJDR['Faixa_Etaria'].map(mapaFaixas)

    st.set_page_config(page_title="Dados - SJDR", page_icon="🏥", layout="wide")
    with st.sidebar:
        st.markdown("## Configurações")
        tamanhoGrafico = st.slider("Altura dos gráficos (px)", 350, 1000, 500)
        st.markdown("---")
        st.markdown("### Filtros")

        with st.expander("Ano"):
            anosDisp = sorted(dfSihsusSJDR['Ano_Competencia'].unique())
            anosSel = st.multiselect(
                "Selecione o(s) Ano(s)", 
                options=anosDisp, 
                default=anosDisp
            )
        
        with st.expander("Faixa Etária"):
            opcoesFaixaEtaria = ['Sem Filtro'] + list(mapaFaixas.values())
            filtroFaixaEtaria = st.radio(
                "Qual filtro você deseja aplicar?",
                opcoesFaixaEtaria
            )

        with st.expander("Sexo"):
            filtroSexo = st.radio(
                "Qual filtro você deseja aplicar?",
                ['Sem Filtro', 'Feminino', 'Masculino']
            )

        with st.expander("Raça/Cor"):
            opcoesRaca = ['Sem Filtro'] + list(mapaRaca.values())
            filtroRaca = st.radio(
                "Qual filtro você deseja aplicar?",
                opcoesRaca
            )

    dfFiltrado = dfSihsusSJDR.copy()

    if filtroFaixaEtaria != "Sem Filtro":
        dfFiltrado = dfFiltrado[dfFiltrado['Faixa_Etaria_Label'] == filtroFaixaEtaria]

    if filtroSexo != "Sem Filtro":
        codigos = mapaSexo[filtroSexo]
        dfFiltrado = dfFiltrado[dfFiltrado['Sexo'].isin(codigos)] 

    if filtroRaca != "Sem Filtro":
        dfFiltrado = dfFiltrado[dfFiltrado['Raca_Cor_Label'] == filtroRaca]

    configGrafico = [None, f"{tamanhoGrafico}px"]

    st.markdown("# Análise de Dados da Base SIHSUS")
    
    GraficoCustoAnual(dfFiltrado, configGrafico, anosSel)
    GraficoFaixaEtaria(dfFiltrado, configGrafico)
    GraficoRaca(dfFiltrado, configGrafico)
    GraficoTendenciaPorFaixaEtaria(dfFiltrado, configGrafico, anosSel)

if __name__ == '__main__':
    main()
