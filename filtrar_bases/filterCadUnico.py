import pandas as pd

input_file = "ICCadUnico\Codigos\DashboardUFSJ\CadUnicoSaoJoaoDelRei.csv"

output_file = "CadUnicoSaoJoaoDelRei_filtrado.csv"

df = pd.read_csv(input_file, dtype=str)  

df_filtrado = df[df["cd_ibge"] == "3162500"]

df_filtrado.to_csv(output_file, index=False, encoding="utf-8")

print(f"\n Arquivo filtrado salvo em: {output_file}")
