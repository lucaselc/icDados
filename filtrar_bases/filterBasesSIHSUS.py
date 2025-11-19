# Filtra a base de dados do SIHSUS do Brasil e extrai TODOS os dados de SJDR
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
# codMunicipio = 316720

# São João Del Rei
codMunicipio = 316250

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

                dfSjdr = df[df['MUNIC_RES'] == codMunicipio]


                if not dfSjdr.empty:
                    dadosFiltrados.append(dfSjdr)

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

    bins = [-1, 14, 24, 44, 64, 200]
    labels = ['A', 'B', 'C', 'D', 'E']
    dfFinal['Faixa_Etaria'] = pd.cut(dfFinal['Idade'], bins=bins, labels=labels)

    diretorioAtual = Path(__file__).parent
    pastaDestino = diretorioAtual.parent / 'database'
    nomeArquivo = 'dadosSihsusSJDR.csv'
    nomeArquivoSaida = pastaDestino / nomeArquivo

    dfFinal.to_csv(nomeArquivoSaida, sep=';', encoding='utf-8-sig', index=False)

else:
    print(f"\n Nenhum registro encontrado para o município do código {codMunicipio}.")