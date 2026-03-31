# Dashboard de Análise de Dados (SIHSUS e SISVAN)

Este projeto apresenta um dashboard interativo desenvolvido em **Python usando Streamlit** para análise de dados sociais e de saúde provenientes do **SIHSUS** e **SISVAN**.

As bases de dados utilizadas estão hospedadas no Google Drive e são baixadas automaticamente na primeira execução.

---

## Requisitos

Instale as dependências necessárias com:

```bash
pip install streamlit streamlit-echarts pandas gdown
```
Para reprocessar a base do sisvan

```bash
pip install pyspark
```
> **Ajuste de performance:** Se estiver usando uma máquina mais potente, aumente `spark.driver.memory` e `spark.sql.shuffle.partitions` na SparkSession para acelerar o processamento.
---

## Como Executar

No terminal, dentro da pasta do projeto, execute:

```bash
streamlit run dashboardV1.py
```

---

## Atualização das Bases de Dados

Se precisar reprocessar os dados a partir dos arquivos originais:

### Organização dos arquivos

* **SIHSUS:** coloque o arquivo `.zip` na raiz do projeto (`icDados/`)
* **SISVAN:** coloque os arquivos `.zip` em:

```
icDados/sisvan/basesSISVAN/
```

### Processamento

Execute os scripts da pasta:

```
filtrar_bases/
```

### Atualização no Dashboard

Após o processamento:

1. Substitua os arquivos antigos no Google Drive pelas novas versões
2. Execute o dashboard novamente

---

## Observação

O dashboard sempre utilizará automaticamente as versões mais recentes das bases disponíveis no Google Drive.
