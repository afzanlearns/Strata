import pandas as p
r = p.read_csv('data/processed/rules_apriori.csv')
q = r[r.antecedents.str.contains('rain') | r.consequents.str.contains('rain')]
q = q[~q.consequents.str.contains('rain:') | q.antecedents.str.contains('rain:')]
print('--- rules with rain consequent or rain+stress ---')
sub = r[(r.consequents.str.contains('rain:')) |
        (r.antecedents.str.contains('rain:') & r.consequents.str.contains('stress|move|depth'))]
print(sub.sort_values('lift', ascending=False).head(10)
      [['antecedents', 'consequents', 'support', 'confidence', 'lift']].to_string(index=False))
print()
print('--- monsoon + rain interaction ---')
sub2 = r[r.antecedents.str.contains('season:monsoon')]
print(sub2.sort_values('lift', ascending=False).head(8)
      [['antecedents', 'consequents', 'support', 'confidence', 'lift']].to_string(index=False))
