import pandas as p
lab = p.read_csv('data/processed/district_labels.csv')
tel = lab[lab.district.isin(
    p.read_csv('data/processed/district_features.csv').district)]
print('mode vs worst25 agreement (telemetry districts):',
      round(float((tel.label == tel.label_worst25).mean()), 3))
print(tel[tel.label != tel.label_worst25][['state', 'district', 'label', 'label_worst25']].to_string(index=False))
