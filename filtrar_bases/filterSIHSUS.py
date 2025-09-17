# Filtra a base de dados do SIHSUS do brasil e extrai o dados de SJDR relacionados a internções dos CIDs estudados
import pandas as pd
import zipfile
from pathlib import Path

diretorioAtual = Path(__file__).parent
caminhoZip = diretorioAtual.parent / 'ETLSIH.zip'

cid_ma_alimentacao = [
    'D50', 'D51', 'D52', 'D53',  
    'E40', 'E41', 'E42', 'E43', 'E44', 'E45', 'E46', 
    'E50', 'E51', 'E52', 'E53', 'E54', 'E55', 'E56',
    'E58', 'E59', 'E60', 'E61', 'E63', 'E64',  
    'E65', 'E66', 'E67', 'E68',  
    'K90'  
]

codigo_municipio = 316250

dados_filtrados = []

with zipfile.ZipFile(caminhoZip, 'r') as zip_ref:
    nomes_arquivos = [f for f in zip_ref.namelist()
                      if f.startswith("ETLSIH.ST_MG_") and f.endswith(".csv")]
    
    for nome_arquivo in nomes_arquivos:
        try:
            print(f"Lendo arquivo: {nome_arquivo}")
            with zip_ref.open(nome_arquivo) as arquivo:
                df = pd.read_csv(arquivo, sep=',', encoding='latin1',
                                 low_memory=False, on_bad_lines='skip')

                df['MUNIC_RES'] = pd.to_numeric(df['MUNIC_RES'], errors='coerce')
                df['DIAG_PRINC'] = df['DIAG_PRINC'].astype(str).str.strip().str.upper()

                df_sjdr = df[df['MUNIC_RES'] == codigo_municipio]

                df_sjdr_filtrado = df_sjdr[df_sjdr['DIAG_PRINC'].str[:3].isin(cid_ma_alimentacao)]

                if not df_sjdr_filtrado.empty:
                    dados_filtrados.append(df_sjdr_filtrado)

        except Exception as e:
            print(f"Erro ao ler {nome_arquivo}: {e}")

if dados_filtrados:
    df_final = pd.concat(dados_filtrados, ignore_index=True)
    
    colunas_desejadas = [
        'ANO_CMPT', 'MES_CMPT', 'N_AIH', 'DT_INTER', 'DT_SAIDA',
        'MUNIC_RES', 'DIAG_PRINC', 'DIAG_SECUN', 'IDADE', 'SEXO',
        'RACA_COR', 'MORTE', 'CAR_INT', 'VAL_TOT'
    ]
    colunas_existentes = [col for col in colunas_desejadas if col in df_final.columns]
    df_final = df_final[colunas_existentes]

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
    df_final.rename(columns=renomear, inplace=True)

    # --- Criar coluna de faixa etária com labels A, B, C, D, E ---
    bins = [-1, 14, 24, 44, 64, 200]   # limites
    labels = ['A', 'B', 'C', 'D', 'E']
    df_final['Faixa_Etaria'] = pd.cut(df_final['Idade'], bins=bins, labels=labels)


    # Salvar no CSV
    df_final.to_csv('dados_sjdr_ma_alimentacao.csv', sep=';', encoding='utf-8-sig', index=False)
    print(f"\n SUCESSO! Arquivo salvo: dados_sjdr_ma_alimentacao.csv com {len(df_final)} registros.")

else:
    print("\n Nenhum registro encontrado após os filtros aplicados.")
