import pyspark.sql.functions as f
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
import zipfile
import tempfile
import shutil
from pathlib import Path
from functools import reduce
import os

# Configuração da Sessão Spark
spark = (
    SparkSession.builder
    .appName("filtrar_sisvan_sjdr_multi_anos") 
    .master("local[*]") 
    .config("spark.sql.shuffle.partitions", "8")  
    .config("spark.driver.memory", "4g")          
    .config("spark.executor.memory", "4g")        
    .config("spark.sql.execution.arrow.pyspark.enabled", "true")  
    .getOrCreate()
)

# --- DEFINIÇÃO DE CAMINHOS ---
base_dir = Path('/media/labmic/HD/Lucas/sisvan/basesSISVAN')

# Definimos uma pasta no SEU HD para servir de área temporária
# Isso evita encher o /tmp do Linux
dir_temporario_hd = base_dir / "temp_processamento"
dir_temporario_hd.mkdir(parents=True, exist_ok=True)

output_filename = 'sisvanSjdr.csv'
final_output_path = base_dir / output_filename
temp_spark_output_dir = base_dir / "temp_spark_output"

dfs_to_union = []
anos = range(2017, 2024)

print("Iniciando processamento dos anos...")

# --- MUDANÇA PRINCIPAL AQUI ---
# Passamos o parâmetro 'dir=' para usar o HD externo como área de extração
with tempfile.TemporaryDirectory(dir=dir_temporario_hd) as temp_dir:
    temp_path = Path(temp_dir)
    
    for ano in anos:
        zip_filename = f'sisvan_estado_nutricional_{ano}.zip'
        csv_filename = f'sisvan_estado_nutricional_{ano}.csv'
        
        file_path_zip = base_dir / zip_filename
        
        if not file_path_zip.exists():
            print(f"Aviso: Arquivo {zip_filename} não encontrado. Pulando...")
            continue
            
        print(f"Extraindo e preparando ano: {ano}...")

        # Extrai o CSV para a pasta temporária criada no HD
        with zipfile.ZipFile(file_path_zip, 'r') as zip_ref:
            zip_ref.extract(csv_filename, path=temp_dir)
        
        extracted_csv_path = temp_path / csv_filename

        # Lê o CSV
        df_ano = spark.read.csv(
            str(extracted_csv_path), 
            header=True, 
            sep=';', 
            encoding='iso-8859-1'
        )
        
        # Filtra para SJDR
        df_sjdr = df_ano.filter(f.col('CO_MUNICIPIO_IBGE') == '316250')
        
        dfs_to_union.append(df_sjdr)

    # --- UNIFICAÇÃO E SALVAMENTO ---
    if dfs_to_union:
        print("Unindo bases de dados e processando (isso pode demorar)...")
        df_final = reduce(DataFrame.unionByName, dfs_to_union)
        
        if temp_spark_output_dir.exists():
            shutil.rmtree(temp_spark_output_dir)

        print("Escrevendo arquivo temporário...")
        (
            df_final.coalesce(1)
            .write
            .option("header", "true")
            .option("sep", ";")
            .option("encoding", "iso-8859-1") 
            .mode('overwrite')
            .csv(str(temp_spark_output_dir))
        )
        
        print("Renomeando para o arquivo final...")
        part_file = next(temp_spark_output_dir.glob('part-*.csv'), None)
        
        if part_file:
            shutil.move(str(part_file), str(final_output_path))
            print(f"Concluído! Arquivo salvo em: {final_output_path}")
            shutil.rmtree(temp_spark_output_dir)
        else:
            print("Erro: Arquivo part-*.csv não encontrado.")
            
    else:
        print("Nenhum dado encontrado.")

# O 'with tempfile...' cuidará de limpar os CSVs extraídos do HD ao final
spark.stop()