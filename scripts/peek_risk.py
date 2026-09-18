import pandas as pd
rk = pd.read_csv('data/processed/crossing_probs.csv')
print('SUNAM-S row:', rk[rk.station == 'Punjab SANGRUR SUNAM SUNAM-S'].to_dict('records'))
print('top risks:')
print(rk.sort_values('cross_prob', ascending=False).head(8).to_string(index=False))
