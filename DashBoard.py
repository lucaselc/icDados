import streamlit as st
from streamlit_echarts import st_echarts
from pathlib import Path
import pandas as pd

def CriarOpcoesGrafico(titulo, nome, data, tipoGrafico):
    options = {} # Inicializa a variável

    # Gráfico de Donut (Rosca)
    # data: [{'value': 1048, 'name': 'Search Engine'}, ...]
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
        
    # Gráfico de Pizza
    # data: [{'value': 1048, 'name': 'Search Engine'}, ...]
    elif tipoGrafico == 'Pizza':
        options = {
            "title": {"text": titulo, "left": "center"},
            "tooltip": {"trigger": "item", "formatter": "<b>{a} <br/>{b}: {c} ({d}%)</b>"},
            "legend": {"top": "5%", "left": "center"},
            "series": [{
                "name": nome,
                "type": "pie",
                "radius": "50%",
                "data": data,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    }
                },
            }],
        }

    # Gráfico de Barras Verticais
    # data: [ ['Mon', 'Tue', ...], [120, 200, ...] ] -> [categorias, valores]
    elif tipoGrafico == 'Barra':
        options = {
            "title": {"text": titulo, "left": "center"},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "legend": {"top": "5%", "left": "center"},
            "xAxis": {"type": "category", "data": data[0]},
            "yAxis": {"type": "value"},
            "series": [{
                "name": nome,
                "data": data[1],
                "type": "bar"
            }],
        }
        
    # --- GRÁFICOS ADICIONADOS ---

    # Gráfico de Linhas
    # data: [ ['Mon', 'Tue', ...], [120, 200, ...] ] -> [categorias, valores]
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
                "smooth": True # Deixa a linha mais suave
            }],
        }
        
    # Gráfico de Barras Horizontais
    # data: [ ['Mon', 'Tue', ...], [120, 200, ...] ] -> [categorias, valores]
    elif tipoGrafico == 'BarraHorizontal':
        options = {
            "title": {"text": titulo, "left": "center"},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "legend": {"top": "5%", "left": "center"},
            "xAxis": {"type": "value"},
            "yAxis": {"type": "category", "data": data[0]},
            "series": [{
                "name": nome,
                "data": data[1],
                "type": "bar"
            }],
        }

    # Gráfico de Boxplot
    # data: [ [655, 850, ...], [700, 830, ...] ] -> lista de listas com os dados de cada categoria
    elif tipoGrafico == 'Boxplot':
        options = {
            "title": [{"text": titulo, "left": "center"}],
            "dataset": [{
                "source": data
                },
                {
                "transform": {
                    "type": "boxplot",
                    "config": {"itemNameFormatter": ""},
                    }
                },
                {"fromDatasetIndex": 1, "fromTransformResult": 1},
                ],
            "tooltip": {"trigger": "item", "axisPointer": {"type": "shadow"}},
            "grid": {"left": "10%", "right": "10%", "bottom": "15%"},
            "xAxis": {
                "type": "category",
                "boundaryGap": True,
                "nameGap": 30,
                "splitArea": {"show": False},
                "splitLine": {"show": False},
                },
            "yAxis": {
                "type": "value",
                "name": nome,
                "splitArea": {"show": True},
                },
            "series": [
                {"name": "boxplot", "type": "boxplot", "datasetIndex": 1},
                {"name": "outlier", "type": "scatter", "datasetIndex": 2},
                ],
            }

    return options


def GraficoCustoAnual(df, configuracoes):
    """
    Cria um gráfico de linhas mostrando a evolução do custo total das internações por ano.
    """
    def filtraDados(df_interno):
        # Agrupa os dados por ano e soma os gastos
        custo_anual = df_interno.groupby('Ano_Competencia')['Valor_Gasto'].sum().round(2)
        
        # Formata os dados para o gráfico de linha: [[anos], [valores]]
        anos = custo_anual.index.tolist()
        valores = custo_anual.values.tolist()
        
        return [anos, valores]

    st.header("Custo Anual com Internações por Má Nutrição")
    
    titulo = "Evolução do Custo Total em São João del-Rei"
    nome_serie = "Custo Total (R$)"
    dados_grafico = filtraDados(df)
    tipo_grafico = 'Linha' # Usando o tipo de gráfico que criamos anteriormente
    
    # Exibe o gráfico usando a função principal
    st_echarts(options=CriarOpcoesGrafico(titulo, nome_serie, dados_grafico, tipo_grafico), height=configuracoes[1])


def GraficoFaixaEtaria(df, configuracoes):
    """
    Cria um gráfico de Donut mostrando a distribuição das internações por faixa etária.
    """
    def filtraDados(df_interno):
        # Mapeamento das letras para labels descritivos
        mapa_faixas = {
            'A': '0-14 anos',
            'B': '15-29 anos',
            'C': '30-44 anos',
            'D': '45-59 anos',
            'E': '60+ anos'
        }
        
        # Conta o número de ocorrências de cada faixa etária
        contagem_faixas = df_interno['Faixa_Etaria'].value_counts()
        
        # Formata os dados para o gráfico de Donut: [{'value': x, 'name': 'y'}, ...]
        dados_formatados = []
        for faixa, contagem in contagem_faixas.items():
            nome_faixa = mapa_faixas.get(faixa, "Não especificada") # Usa o mapa para obter o nome
            dados_formatados.append({"value": contagem, "name": nome_faixa})
            
        return dados_formatados

    st.header("Distribuição de Internações por Faixa Etária")
    
    titulo = "Internações por Faixa Etária em São João del-Rei"
    nome_serie = "Nº de Internações"
    dados_grafico = filtraDados(df)
    tipo_grafico = 'Donut' # Usando o gráfico de Donut como no seu exemplo
    
    # Exibe o gráfico
    st_echarts(options=CriarOpcoesGrafico(titulo, nome_serie, dados_grafico, tipo_grafico), height=configuracoes[1])




def main():
    try:
        diretorioAtual = Path(__file__).parent
        caminhoArquivo = diretorioAtual / 'database' / 'sihsusSJDR.csv'
        dfsihsusSJDR = pd.read_csv(caminhoArquivo, sep=';')
        
        dfsihsusSJDR['Valor_Gasto'] = dfsihsusSJDR['Valor_Gasto'].astype(str).str.replace(',', '.').astype(float)
    
    except FileNotFoundError:
        st.error("Erro: O arquivo de dados não foi encontrado")
        st.stop() 

    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar ou processar os dados: {e}")
        st.stop()

    st.set_page_config(
        page_title="Dados - SJDR",
        page_icon="🏥",
        initial_sidebar_state="expanded",
        layout="wide",
    )

    with st.sidebar:
        st.markdown("<h1 style='text-align: center;'>Configurações</h1>", unsafe_allow_html=True)

        with st.expander("Aparência dos Gráficos"):
            tamanho_grafico = st.slider("Altura dos gráficos (pixels)", min_value=350, max_value=1000, value=500)

    st.markdown("<h1 style='text-align: center;'>Análise de Custos com Internações por Má Nutrição em São João del-Rei</h1>", unsafe_allow_html=True)
    st.markdown("---")


    configuracoes_grafico = [None, f"{tamanho_grafico}px"]
    
    GraficoCustoAnual(dfsihsusSJDR, configuracoes_grafico)
    GraficoFaixaEtaria(dfsihsusSJDR, configuracoes_grafico)


if __name__ == '__main__':
    main()