import pandas as pd
import zipfile
from pathlib import Path
import io  
import traceback 

DIRETORIO_ATUAL = Path(__file__).parent
NOME_ARQUIVO_ZIP = 'sisvan_estado_nutricional_2022.zip'
CAMINHO_ZIP = DIRETORIO_ATUAL / NOME_ARQUIVO_ZIP

CODIGO_MUNICIPIO_SJDR = 316250
ANO_REFERENCIA = 2022

NOME_ARQUIVO_SAIDA = f'sisvan_tratado_SJDR_{ANO_REFERENCIA}.csv'
CAMINHO_SAIDA = DIRETORIO_ATUAL / NOME_ARQUIVO_SAIDA

COLUNAS_SELECIONADAS = [
    'CO_ACOMPANHAMENTO', 'CO_PESSOA_SISVAN', 'CO_MUNICIPIO_IBGE', 'CO_CNES',
    'DT_ACOMPANHAMENTO', 'NU_COMPETENCIA', 'NU_FASE_VIDA', 'DS_FASE_VIDA',
    'SG_SEXO', 'CO_RACA_COR', 'DS_RACA_COR', 'NU_PESO', 'NU_ALTURA', 'DS_IMC',
    'PESO X IDADE', 'PESO X ALTURA', 'CRI. ALTURA X IDADE', 'CRI. IMC X IDADE',
    'ADO. ALTURA X IDADE', 'ADO. IMC X IDADE', 'CO_ESTADO_NUTRI_ADULTO',
    'CO_ESTADO_NUTRI_IDOSO', 'CO_SISTEMA_ORIGEM_ACOMP', 'DS_SISTEMA_ORIGEM_ACOMP',
]

print(f"Iniciando tratamento dos dados do SISVAN para São João del Rei ({ANO_REFERENCIA}).")
print(f"Lendo arquivo ZIP: {CAMINHO_ZIP}")

lista_dfs_filtrados = []

try:
    with zipfile.ZipFile(CAMINHO_ZIP, 'r') as zip_ref:
        nomes_arquivos_csv = [f for f in zip_ref.namelist() if f.lower().endswith(".csv")]
        total_arquivos = len(nomes_arquivos_csv)
        print(f"Encontrados {total_arquivos} arquivos CSV dentro do ZIP.")

        for i, nome_arquivo in enumerate(nomes_arquivos_csv, 1):
            print(f"  Processando arquivo {i}/{total_arquivos}: {nome_arquivo}...")
            try:
                with zip_ref.open(nome_arquivo) as arquivo_bytes:
                    # Guardar os bytes para tentar diferentes encodings
                    bytes_content = arquivo_bytes.read()
                    df_temp = None # Inicializa df_temp como None
                    try:
                        df_temp = pd.read_csv(io.BytesIO(bytes_content), sep=',', encoding='utf-8', low_memory=False)
                        print("    -> Lido com encoding utf-8")
                    except UnicodeDecodeError:
                        try:
                            df_temp = pd.read_csv(io.BytesIO(bytes_content), sep=',', encoding='latin1', low_memory=False)
                            print("    -> Lido com encoding latin1")
                        except UnicodeDecodeError:
                            try:
                                df_temp = pd.read_csv(io.BytesIO(bytes_content), sep=',', encoding='cp1252', low_memory=False)
                                print("    -> Lido com encoding cp1252")
                            except UnicodeDecodeError as enc_err:
                                print(f"    -> ERRO DE ENCODING: Não foi possível ler com utf-8, latin1 ou cp1252. Erro: {enc_err}")
                                continue # Pula para o próximo arquivo CSV se não conseguir ler

                    # Verifica se df_temp foi carregado antes de prosseguir
                    if df_temp is None:
                         continue # Pula para o próximo arquivo se houve erro de leitura

                    # --- Filtragem ---
                    # Verifica se a coluna existe antes de tentar acessá-la
                    if 'CO_MUNICIPIO_IBGE' not in df_temp.columns:
                        print(f"    -> ERRO: Coluna 'CO_MUNICIPIO_IBGE' não encontrada no arquivo {nome_arquivo}.")
                        continue # Pula para o próximo arquivo

                    df_temp['CO_MUNICIPIO_IBGE'] = pd.to_numeric(df_temp['CO_MUNICIPIO_IBGE'], errors='coerce')
                    df_temp.dropna(subset=['CO_MUNICIPIO_IBGE'], inplace=True)
                    df_temp['CO_MUNICIPIO_IBGE'] = df_temp['CO_MUNICIPIO_IBGE'].astype(int)

                    df_filtrado_municipio = df_temp[df_temp['CO_MUNICIPIO_IBGE'] == CODIGO_MUNICIPIO_SJDR]

                    if not df_filtrado_municipio.empty:
                        # Seleciona apenas as colunas desejadas ANTES de adicionar à lista
                        colunas_presentes = [col for col in COLUNAS_SELECIONADAS if col in df_filtrado_municipio.columns]
                        lista_dfs_filtrados.append(df_filtrado_municipio[colunas_presentes])
                        print(f"    -> {len(df_filtrado_municipio)} registros encontrados e adicionados para SJDR.")
                    else:
                        print(f"    -> Nenhum registro para SJDR neste arquivo.")

            except Exception as e:
                print(f"    -> ERRO DETALHADO ao processar o arquivo {nome_arquivo}:")
                traceback.print_exc()

except FileNotFoundError:
    print(f"ERRO CRÍTICO: Arquivo ZIP '{NOME_ARQUIVO_ZIP}' não encontrado no diretório '{DIRETORIO_ATUAL}'.")
    exit()
except zipfile.BadZipFile:
    print(f"ERRO CRÍTICO: O arquivo ZIP '{NOME_ARQUIVO_ZIP}' parece estar corrompido.")
    exit()
except Exception as e:
    print(f"ERRO CRÍTICO inesperado ao lidar com o arquivo ZIP: {e}")
    exit()

if not lista_dfs_filtrados:
    print(f"\nNenhum registro encontrado para São João del Rei (Código: {CODIGO_MUNICIPIO_SJDR}) em {ANO_REFERENCIA} após processar todos os arquivos.")
else:
    print(f"\nConsolidando dados de {len(lista_dfs_filtrados)} partes...")
    try:
        df_final = pd.concat(lista_dfs_filtrados, ignore_index=True)
        print(f"Total de registros brutos consolidados para SJDR: {len(df_final)}")

        # Seleciona apenas as colunas de interesse que existem no DataFrame final
        # (Redundante se já selecionado antes, mas garante consistência)
        colunas_existentes_final = [col for col in COLUNAS_SELECIONADAS if col in df_final.columns]
        df_final = df_final[colunas_existentes_final]

        print("Realizando tratamento final dos dados (conversão de tipos)...")

        # --- Tratamento de Tipos de Dados ---
        if 'DT_ACOMPANHAMENTO' in df_final.columns:
            df_final['DT_ACOMPANHAMENTO'] = pd.to_datetime(df_final['DT_ACOMPANHAMENTO'], errors='coerce')

        colunas_numericas = ['NU_PESO', 'NU_ALTURA', 'DS_IMC']
        for col in colunas_numericas:
            if col in df_final.columns:
                if df_final[col].dtype == 'object':
                     df_final[col] = df_final[col].str.replace(',', '.', regex=False)
                df_final[col] = pd.to_numeric(df_final[col], errors='coerce')

        colunas_inteiras = [
            'NU_FASE_VIDA', 'CO_RACA_COR', 'CO_ESTADO_NUTRI_ADULTO',
            'CO_ESTADO_NUTRI_IDOSO', 'CO_SISTEMA_ORIGEM_ACOMP',
            'PESO X IDADE', 'PESO X ALTURA', 'CRI. ALTURA X IDADE', 'CRI. IMC X IDADE',
            'ADO. ALTURA X IDADE', 'ADO. IMC X IDADE' # Adiciona colunas de classificação aqui
        ]
        for col in colunas_inteiras:
             if col in df_final.columns:
                  # Tenta converter para float primeiro para lidar com possíveis decimais (ex: '1.0')
                  numeric_col = pd.to_numeric(df_final[col], errors='coerce')
                  # Converte para Int64 que aceita NaN
                  df_final[col] = numeric_col.astype('Int64')


        if 'DT_ACOMPANHAMENTO' in df_final.columns:
             df_final.dropna(subset=['DT_ACOMPANHAMENTO'], inplace=True)

        try:
            df_final.to_csv(CAMINHO_SAIDA, sep=';', encoding='utf-8-sig', index=False)
            print(f"\nSUCESSO! Dados tratados salvos em:")
            print(CAMINHO_SAIDA)
            print(f"Total de registros finais: {len(df_final)}")
        except Exception as e:
            print(f"\nERRO ao salvar o arquivo CSV final: {e}")

    except Exception as concat_err:
        print(f"\nERRO ao concatenar os DataFrames filtrados: {concat_err}")

