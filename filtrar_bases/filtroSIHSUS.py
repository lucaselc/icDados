import pandas as pd
import zipfile
from pathlib import Path

diretorioAtual = Path(__file__).parent
caminhoZip = diretorioAtual.parent / 'ETLSIH.zip'
pastaDestino = diretorioAtual.parent / 'database'

# Dicionário com Nome da Cidade (para o arquivo) e Código (para o filtro)
# Adicione ou remova cidades aqui conforme necessário
municipios_alvo = {
    'OuroBranco': 314590,
    'Divinopolis': 312230,
    'SeteLagoas': 316720,
    'SaoJoaoDelRei': 316250
}

# Lista de CIDs de interesse
codigos_cid = [
    'A00', 'A01', 'A02', 'A03', 'A04', 'A05', 'A07', 'A08','A09',
    'D50', 'D51', 'D52', 'D53',  
    'E40', 'E41', 'E42', 'E43', 'E44', 'E45', 'E46', 
    'E50', 'E51', 'E52', 'E53', 'E54', 'E55', 'E56',
    'E58', 'E59', 'E60', 'E61', 'E63',  'E64'
    'E11', 'E66', 'E78', 'I10', 'I20', 'I25', 'I60', 'I69',
    'C00', 'C14', 'C18', 'C20', 'C15', 'C16', 'C22', 'C25',
    'N18',
    'K90'  
]

# Dicionário para armazenar temporariamente os DataFrames de cada cidade

dados_coletados = {cod: [] for cod in municipios_alvo.values()}


with zipfile.ZipFile(caminhoZip, 'r') as zip_ref:
    nomesArquivos = [f for f in zip_ref.namelist()
                     if f.startswith("ETLSIH.ST_MG_") and f.endswith(".csv")]

    for nomeArquivo in nomesArquivos:
        try:
            with zip_ref.open(nomeArquivo) as arquivo:
                df = pd.read_csv(arquivo, sep=',', encoding='latin1',
                                 low_memory=False, on_bad_lines='skip')

                df['MUNIC_RES'] = pd.to_numeric(df['MUNIC_RES'], errors='coerce')
                df = df[df['MUNIC_RES'].isin(municipios_alvo.values())]

                if df.empty:
                    continue # Pula se não tiver ninguém das cidades alvo neste arquivo

                df['DIAG_PRINC'] = df['DIAG_PRINC'].astype(str).str.strip().str.upper()

                df = df[df['DIAG_PRINC'].str[:3].isin(codigos_cid)]

                if df.empty:
                    continue

                for cod_municipio in municipios_alvo.values():
                    df_cidade = df[df['MUNIC_RES'] == cod_municipio]
                    if not df_cidade.empty:
                        dados_coletados[cod_municipio].append(df_cidade)

        except Exception as e:
            print(f"Erro ao ler {nomeArquivo}: {e}")



for nome_cidade, cod_municipio in municipios_alvo.items():
    lista_dfs = dados_coletados[cod_municipio]
    
    if lista_dfs:
        
        dfFinal = pd.concat(lista_dfs, ignore_index=True)

        colunas = [
            'ANO_CMPT', 'MES_CMPT', 'N_AIH', 'DT_INTER', 'DT_SAIDA',
            'MUNIC_RES', 'DIAG_PRINC', 'DIAG_SECUN', 'IDADE', 'SEXO',
            'RACA_COR', 'MORTE', 'CAR_INT', 'VAL_TOT'
        ]
        colunasExistentes = [col for col in colunas if col in dfFinal.columns]
        dfFinal = dfFinal[colunasExistentes]

        renomear = {
            'ANO_CMPT': 'Ano_Competencia',
            'MES_CMPT': 'Mes_Competencia',
            'N_AIH': 'Numero_AIH',
            'DT_INTER': 'Data_Internacao',
            'DT_SAIDA': 'Data_Saida',
            'MUNIC_RES': 'Municipio_Residencia',
            'DIAG_PRINC': 'CID10_Principal',
            'DIAG_SECUN': 'CID10_Secundario',
            'IDADE': 'Idade',
            'SEXO': 'Sexo',
            'RACA_COR': 'Raca_Cor',
            'MORTE': 'Morte',
            'CAR_INT': 'Carater_Internacao',
            'VAL_TOT': 'Valor_Gasto'
        }
        dfFinal.rename(columns=renomear, inplace=True)

        # Criar coluna de faixa etária
        bins = [-1, 14, 24, 44, 64, 200]
        labels = ['A', 'B', 'C', 'D', 'E']
        dfFinal['Faixa_Etaria'] = pd.cut(dfFinal['Idade'], bins=bins, labels=labels)

        nomeArquivoSaida = pastaDestino / f'dadosFiltrados{nome_cidade}.csv'
        
        # Garante que a pasta destino existe
        pastaDestino.mkdir(parents=True, exist_ok=True)

        dfFinal.to_csv(nomeArquivoSaida, sep=';', encoding='utf-8-sig', index=False)
    else:
        print(f"Nenhum dado encontrado para {nome_cidade} (Cód: {cod_municipio}). Arquivo não gerado.")

