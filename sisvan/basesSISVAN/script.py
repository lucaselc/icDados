import pandas as pd
import os

# --- CORREÇÃO DO CAMINHO ---
# Pega o caminho absoluto da pasta onde ESTE script (.py) está salvo
diretorio_do_script = os.path.dirname(os.path.abspath(__file__))

nome_arquivo_entrada = 'sisvanSjdr.csv'
nome_arquivo_saida = 'sisvanSjdr_padronizado.csv'

# Monta o caminho completo usando a pasta do script como base
caminho_entrada = os.path.join(diretorio_do_script, nome_arquivo_entrada)
caminho_saida = os.path.join(diretorio_do_script, nome_arquivo_saida)

# --- DEBUG (Para você conferir) ---
print(f"Pasta do script: {diretorio_do_script}")
print(f"Procurando arquivo em: {caminho_entrada}")

# --- PROCESSAMENTO ---

# 1. Carregar o CSV
try:
    df = pd.read_csv(caminho_entrada, sep=';', encoding='iso-8859-1', dtype=str)
    print("Arquivo carregado com sucesso!")
except FileNotFoundError:
    print(f"\nERRO CRÍTICO: O arquivo ainda não foi encontrado.")
    print(f"Verifique se o nome '{nome_arquivo_entrada}' está exatamente igual na pasta.")
    # Dica: Às vezes o Windows esconde a extensão e o arquivo chama 'sisvanSjdr.csv.csv'
    exit()

# 2. Lista de colunas para corrigir
colunas_para_corrigir = [
    'NU_PESO', 
    'NU_ALTURA', 
    'DS_IMC', 
    'NU_FASE_VIDA'
]

print("Padronizando colunas...")

for col in colunas_para_corrigir:
    if col in df.columns:
        # Substitui vírgula por ponto
        df[col] = df[col].str.replace(',', '.', regex=False)
        # Converte para numérico
        df[col] = pd.to_numeric(df[col], errors='coerce')
    else:
        print(f"Aviso: Coluna '{col}' não encontrada.")

# 3. Salvar
print(f"Salvando em: {caminho_saida}")
df.to_csv(caminho_saida, sep=';', index=False, encoding='iso-8859-1')
print("Concluído.")