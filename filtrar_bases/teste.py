# Filtra a base de dados do SIHSUS do brasil e extrai o dados de SJDR relacionados a internções dos CIDs estudados
import pandas as pd
import zipfile
from pathlib import Path

diretorioAtual = Path(__file__).parent
caminhoZip = diretorioAtual.parent / 'ETLSIH.zip'

#cada linha abaixo refere a um muncipio, caso queira extrair a base do municipio, altere o código ou descomente o municipio

# Ouro branco
#codMunicipio = 314590

# Divinopolis
#codMunicipio = 312230

# Sete Lagoas
#codMunicipio = 316720

# teste sete lagoas
#codMunicipio = 3167202


# São João Del Rei
codMunicipio = 316250



codigos = [
    'D50', 'D51', 'D52', 'D53',
    'E40', 'E41', 'E42', 'E43', 'E44', 'E45', 'E46',
    'E50', 'E51', 'E52', 'E53', 'E54', 'E55', 'E56',
    'E58', 'E59', 'E60', 'E61', 'E63', 'E64',
    'K90', 
    'E65', 'E66', 'E67', 'E68',
    'E10', 'E11', 'E12', 'E13', 'E14',
    'I10', 'I11', 'I12', 'I13', 'I15',
    'E78', 
    'E88', 
]


dadosFiltrados = []

with zipfile.ZipFile(caminhoZip, 'r') as zip_ref:
    nomesArquivos = [f for f in zip_ref.namelist()
                      if f.startswith("ETLSIH.ST_MG_") and f.endswith(".csv")]

    for nomeArquivo in nomesArquivos:
        try:
            print(f"Lendo arquivo: {nomeArquivo}")
            with zip_ref.open(nomeArquivo) as arquivo:
                df = pd.read_csv(arquivo, sep=',', encoding='latin1',
                                 low_memory=False, on_bad_lines='skip')

                df['MUNIC_RES'] = pd.to_numeric(df['MUNIC_RES'], errors='coerce')
                # Adicionado dropna após conversão para evitar erros com NaN na comparação
                df.dropna(subset=['MUNIC_RES'], inplace=True)
                df['MUNIC_RES'] = df['MUNIC_RES'].astype(int)
                df['DIAG_PRINC'] = df['DIAG_PRINC'].astype(str).str.strip().str.upper()

                dfSjdr = df[df['MUNIC_RES'] == codMunicipio]

                dfSjdrFiltrado = dfSjdr[dfSjdr['DIAG_PRINC'].str[:3].isin(codigos)]

                if not dfSjdrFiltrado.empty:
                    dadosFiltrados.append(dfSjdrFiltrado)

        except Exception as e:
            print(f"Erro ao ler {nomeArquivo}: {e}")

if dadosFiltrados:
    dfFinal = pd.concat(dadosFiltrados, ignore_index=True)

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

    # Adicionado tratamento de erro para coluna Idade antes do pd.cut
    dfFinal['Idade'] = pd.to_numeric(dfFinal['Idade'], errors='coerce')
    dfFinal.dropna(subset=['Idade'], inplace=True) # Remove linhas onde Idade não é número
    dfFinal['Idade'] = dfFinal['Idade'].astype(int)

    bins = [-1, 14, 24, 44, 64, 200]   # limites 
    labels = ['A', 'B', 'C', 'D', 'E']
    dfFinal['Faixa_Etaria'] = pd.cut(dfFinal['Idade'], bins=bins, labels=labels, right=True)


    # Salvar no CSV
    diretorioAtual = Path(__file__).parent
    pastaDestino = diretorioAtual.parent / 'database'
    nomeArquivo = 'TesteSJDRs.csv'
    nomeArquivoSaida = pastaDestino / nomeArquivo
    

    dfFinal.to_csv(nomeArquivoSaida, sep=';', encoding='utf-8-sig', index=False)
    print(f"\n SUCESSO! Arquivo salvo: {nomeArquivoSaida.name} com {len(dfFinal)} registros.")


else:
    print(f"\n Nenhum registro encontrado para o município do código {codMunicipio} com os CIDs especificados.")

