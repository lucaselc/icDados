import pyspark.sql.functions as f
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
import zipfile
import tempfile
import shutil
import pandas as pd
from pathlib import Path
from functools import reduce

#configuração conforme a maquina 
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


diretorio_atual       = Path(__file__).parent 
base_dir              = diretorio_atual.parent / 'sisvan' / 'basesSISVAN'  # onde ficará os arquivos .zip de cada ano do sisvan
dir_database          = diretorio_atual.parent / 'database'                # onde ficará armazenado
dir_database.mkdir(parents=True, exist_ok=True)

dir_temporario        = base_dir / "temp_processamento"
dir_temporario.mkdir(parents=True, exist_ok=True)

final_output_path     = dir_database / 'sisvanSjdr.csv'
temp_spark_output_dir = base_dir / "temp_spark_output"

COLUNAS_NUMERICAS = ['NU_PESO', 'NU_ALTURA', 'DS_IMC', 'NU_FASE_VIDA']

dfs_to_union = []


with tempfile.TemporaryDirectory(dir=dir_temporario) as temp_dir:
    temp_path = Path(temp_dir)

    for ano in range(2008, 2024):
        zip_filename = f'sisvan_estado_nutricional_{ano}.zip'
        csv_filename = f'sisvan_estado_nutricional_{ano}.csv'
        file_path_zip = base_dir / zip_filename

        if not file_path_zip.exists():
            continue

        print(f"  Extraindo e filtrando: {ano}...")

        with zipfile.ZipFile(file_path_zip, 'r') as zip_ref:
            zip_ref.extract(csv_filename, path=temp_dir)

        df_ano = spark.read.csv(
            str(temp_path / csv_filename),
            header=True,
            sep=';',
            encoding='iso-8859-1'
        )

        dfs_to_union.append(
            df_ano.filter(f.col('CO_MUNICIPIO_IBGE') == '316250')
        )

    # união
    if not dfs_to_union:
        print("Nenhum dado encontrado.")
        spark.stop()
        raise SystemExit

    df_final = reduce(DataFrame.unionByName, dfs_to_union)

    if temp_spark_output_dir.exists():
        shutil.rmtree(temp_spark_output_dir)

    (
        df_final.coalesce(1)
        .write
        .option("header", "true")
        .option("sep", ";")
        .option("encoding", "iso-8859-1")
        .mode("overwrite")
        .csv(str(temp_spark_output_dir))
    )

    part_file = next(temp_spark_output_dir.glob('part-*.csv'), None)
    if not part_file:
        print("Erro: arquivo part-*.csv não encontrado.")
        spark.stop()
        raise SystemExit

    shutil.move(str(part_file), str(final_output_path))
    shutil.rmtree(temp_spark_output_dir)

spark.stop()

df = pd.read_csv(final_output_path, sep=';', encoding='iso-8859-1', dtype=str)

for col in COLUNAS_NUMERICAS:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].str.replace(',', '.', regex=False), errors='coerce')
    else:
        print(f"  Aviso: coluna '{col}' não encontrada.")

df.to_csv(final_output_path, sep=';', index=False, encoding='iso-8859-1')

print(f"Concluído! Arquivo final: {final_output_path}")
