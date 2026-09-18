import pandas as p
d = p.read_csv('data/processed/district_features.csv')
cols = ['state', 'district', 'n_stations', 'median_depth',
        'annual_decline_m_per_year', 'frac_deepening']
print(d[cols].sort_values('frac_deepening').to_string())
print()
s = p.read_csv('data/processed/station_features.csv')
print('stations:', len(s), '| deepening:', int((s.annual_decline_m_per_year > 0).sum()),
      '| recovering:', int((s.annual_decline_m_per_year < 0).sum()),
      '| datum_shift stations:', int(s.datum_shift.sum()))
print('median_depth by state:'); print(s.groupby('state').median_depth.median())
print('monsoon_delta by state (neg=recovery):'); print(s.groupby('state').monsoon_delta_m.median())
