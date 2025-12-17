import pyspark.sql.functions as f
from pyspark.sql import SparkSession
import zipfile
import tempfile
import os

spark = (
    SparkSession.builder
    .appName("filtrar_sisvan_sjdr") 
    .master("local[*]") 
    .config("spark.sql.shuffle.partitions", "8")  
    .config("spark.driver.memory", "4g")          
    .config("spark.executor.memory", "4g")        
    .config("spark.sql.execution.arrow.pyspark.enabled", "true")  
    .getOrCreate()
)


zip_file_path = '/media/labmic/HD/Lucas/sisvan/basesSISVAN/sisvan_estado_nutricional_2017.zip' 

csv_file_name_inside_zip = 'sisvan_estado_nutricional_2017.csv'

output_path = '/media/labmic/HD/Lucas/sisvan/basesSISVAN/filtrado_sjdr_csv'


with tempfile.TemporaryDirectory() as temp_dir:
    
    extracted_csv_path = os.path.join(temp_dir, csv_file_name_inside_zip)
    
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extract(csv_file_name_inside_zip, path=temp_dir)
        

    df_sisvan_zip = spark.read.csv(
        extracted_csv_path, 
        header=True, 
        sep=';', 
        encoding='iso-8859-1'
    )
    
    
    
    df_sjdr = df_sisvan_zip.filter(f.col('CO_MUNICIPIO_IBGE') == '316250')
    
    
    (
        df_sjdr.coalesce(1)
        .write
        .option("header", "true")
        .option("sep", ";")
        .option("encoding", "iso-8859-1") 
        .mode('overwrite')
        .csv(output_path)
    )
    


spark.stop()