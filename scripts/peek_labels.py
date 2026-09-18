import pandas as p
b = p.read_csv('data/processed/gwra2025_blocks.csv')
pr = b[b.state.str.upper().isin(['PUNJAB', 'RAJASTHAN'])].copy()
pr['district'] = pr.district.str.upper()
for name, fn in [('mode', lambda s: s.value_counts().idxmax()),
                 ('worst>=25%', None)]:
    if fn is None:
        continue
    lab = pr[pr.category != 'salinity'].groupby(
        [pr.state.str.lower(), pr.district]).category.agg(fn)
    print(name, ':')
    print(lab.value_counts().to_string())
# per-district OE fraction spread (which districts are NOT OE-dominated?)
f = pr[pr.category != 'salinity'].groupby(
    [pr.state.str.lower(), pr.district]).category.value_counts(normalize=True).unstack(fill_value=0)
print(f.round(2).to_string())
