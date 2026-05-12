import pandas as pd
df = pd.read_csv('phase-a/testset_v1.csv')
col_map = {'user_input':'question','reference':'ground_truth','reference_contexts':'contexts','synthesizer_name':'evolution_type'}
df = df.rename(columns={k:v for k,v in col_map.items() if k in df.columns})
df.to_csv('phase-a/testset_v1.csv', index=False)
print('Columns:', df.columns.tolist())
print('Rows:', len(df))
