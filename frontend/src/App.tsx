import { useEffect, useState } from 'react';
import './index.css';
import { api } from './api';
import type { District, DistrictDetail, StationDetail } from './api';

const LABEL_HINT: Record<string, string> = {
  safe: 'SAFE', semi_critical: 'SEMI-CRIT', critical: 'CRITICAL', over_exploited: 'OVER-EXPLOITED',
};

function Chip({ label }: { label: string }) {
  return <span className={`chip ${label}`}>{LABEL_HINT[label] ?? label}</span>;
}

function TrendChart({ series, forecast }: {
  series: { date: string; depth: number }[];
  forecast: { date: string; actual: number; predicted: number }[];
}) {
  const W = 640, H = 220, P = 32;
  const pts = series.slice(-160);
  const all = [...pts.map(p => p.depth), ...forecast.map(f => f.predicted)];
  if (!pts.length) return <p>NO SERIES DATA</p>;
  const lo = Math.min(...all), hi = Math.max(...all), span = hi - lo || 1;
  const X = (i: number, n: number) => P + (i / Math.max(1, n - 1)) * (W - 2 * P);
  const Y = (v: number) => H - P - ((v - lo) / span) * (H - 2 * P);
  const line = (vals: number[]) => vals.map((v, i) => `${X(i, vals.length)},${Y(v)}`).join(' ');
  const fx = (i: number) => X(pts.length - forecast.length + i, pts.length);
  const fline = forecast.map((f, i) => `${fx(i)},${Y(f.predicted)}`).join(' ');
  const fdate = forecast.map(f => f.date.slice(0, 10)).join(',');
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ border: '2px solid #111', background: '#fff' }}>
      <text x={P} y={14} fontSize="10">DEPTH m (LARGER = DEEPER = WORSE) — range {lo.toFixed(0)}–{hi.toFixed(0)}</text>
      <polyline points={line(pts.map(p => p.depth))} fill="none" stroke="#111" strokeWidth="2" />
      {forecast.length > 0 && (
        <polyline points={fline} fill="none" stroke="#ff4d00" strokeWidth="2" strokeDasharray="5 3" />
      )}
      <text x={P} y={H - 8} fontSize="10">— OBSERVED &nbsp;&nbsp; - - FORECAST (30D) &nbsp;&nbsp; last: {fdate.split(',').pop() ?? ''}</text>
    </svg>
  );
}

export default function App() {
  const [summary, setSummary] = useState<Awaited<ReturnType<typeof api.summary>> | null>(null);
  const [districts, setDistricts] = useState<District[]>([]);
  const [stateF, setStateF] = useState('');
  const [selD, setSelD] = useState<{ state: string; district: string } | null>(null);
  const [detail, setDetail] = useState<DistrictDetail | null>(null);
  const [station, setStation] = useState<StationDetail | null>(null);
  const [similar, setSimilar] = useState<{ station: string; distance: number }[]>([]);
  const [rules, setRules] = useState<Awaited<ReturnType<typeof api.rules>>>([]);
  const [alerts, setAlerts] = useState<Awaited<ReturnType<typeof api.alerts>>>([]);

  useEffect(() => {
    api.summary().then(setSummary).catch(() => setSummary(null));
    api.rules().then(setRules).catch(() => {});
    api.alerts().then(setAlerts).catch(() => {});
  }, []);
  useEffect(() => {
    api.districts(stateF || undefined).then(setDistricts).catch(() => {});
  }, [stateF]);
  useEffect(() => {
    if (!selD) { setDetail(null); setStation(null); return; }
    api.district(selD.state, selD.district).then(d => { setDetail(d); setStation(null); }).catch(() => {});
  }, [selD]);
  const openStation = (name: string) => {
    api.station(name).then(s => {
      setStation(s);
      api.similar(name).then(setSimilar).catch(() => {});
    }).catch(() => {});
  };

  return (
    <>
      <header>
        <h1><span>STRATA</span> GROUNDWATER RESOURCE EVALUATION</h1>
        <p>SIH25068 · PUNJAB + RAJASTHAN · DWLR 2022–2025
          {summary && ` · ${summary.stations} STATIONS / ${summary.districts} DISTRICTS / ${summary.anomalies} ANOMALIES`}</p>
      </header>
      <div className="layout">
        <div className="panel">
          <h2>DISTRICTS</h2>
          <div className="body">
            <select value={stateF} onChange={e => setStateF(e.target.value)} style={{ width: '100%', marginBottom: 8 }}>
              <option value="">ALL STATES</option>
              <option value="punjab">PUNJAB</option>
              <option value="rajasthan">RAJASTHAN</option>
            </select>
            {districts.map(d => (
              <button key={d.state + d.district} className={`rowbtn${selD?.district === d.district ? ' active' : ''}`}
                onClick={() => setSelD({ state: d.state, district: d.district })}>
                <Chip label={d.label} /> {d.district} <small>({d.n_stations})</small>
              </button>
            ))}
          </div>
        </div>

        <div className="panel">
          <h2>{station ? 'STATION' : detail ? 'DISTRICT' : 'SELECT A DISTRICT'}</h2>
          <div className="body">
            {!detail && <p>Pick a district on the left. Pick a station to see trend, forecast, crossing risk, similar wells, anomaly flags.</p>}
            {detail && !station && (
              <>
                <h3 style={{ margin: '0 0 4px' }}>{detail.district} <Chip label={detail.label} /></h3>
                <dl className="kv">
                  <dt>stations</dt><dd>{detail.n_stations}</dd>
                  <dt>median depth</dt><dd>{detail.median_depth?.toFixed(1)} m</dd>
                  <dt>annual decline</dt><dd className={detail.annual_decline > 0 ? 'neg' : 'pos'}>{detail.annual_decline?.toFixed(2)} m/yr</dd>
                  <dt>deepening share</dt><dd>{(detail.frac_deepening * 100)?.toFixed(0)}%</dd>
                </dl>
                <table>
                  <thead><tr><th>STATION</th><th>DEPTH</th><th>Δ/yr</th><th>FLAG</th></tr></thead>
                  <tbody>
                    {detail.stations.map(s => (
                      <tr key={s.station}>
                        <td><button className="rowbtn" onClick={() => openStation(s.station)}>{s.station}</button></td>
                        <td>{s.median_depth?.toFixed(1)}</td>
                        <td className={s.annual_decline > 0 ? 'neg' : 'pos'}>{s.annual_decline?.toFixed(2)}</td>
                        <td>{s.if_flag ? '⚠ ANOMALY' : `C${s.kmeans}`}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </>
            )}
            {station && (
              <>
                <button onClick={() => setStation(null)}>← BACK TO {station.district}</button>
                <h3 style={{ margin: '8px 0 4px' }}>{station.station} <Chip label={station.label} /></h3>
                <dl className="kv">
                  <dt>median depth</dt><dd>{station.median_depth?.toFixed(1)} m</dd>
                  <dt>annual decline</dt><dd className={station.annual_decline > 0 ? 'neg' : 'pos'}>{station.annual_decline?.toFixed(2)} m/yr</dd>
                  <dt>monsoon Δ</dt><dd>{station.monsoon_delta?.toFixed(2)} m (neg = recovery)</dd>
                  <dt>cluster</dt><dd>C{station.kmeans} archetype</dd>
                  <dt>anomaly</dt><dd>{station.if_flag ? `⚠ FLAGGED (score ${station.if_score?.toFixed(2)})` : 'none'}</dd>
                  <dt>90-day crossing risk</dt>
                  <dd><span className={station.risk >= 0.235 ? 'risk-high' : 'risk-low'}>
                    {(station.risk * 100).toFixed(1)}% {station.risk >= 0.235 ? 'HIGH' : 'LOW'}</span></dd>
                </dl>
                <TrendChart series={station.series} forecast={station.forecast} />
                <h4>SIMILAR STATIONS (EUCLIDEAN, BEHAVIOUR SPACE)</h4>
                <table>
                  <thead><tr><th>STATION</th><th>DIST</th></tr></thead>
                  <tbody>{similar.map(s => (
                    <tr key={s.station}><td><button className="rowbtn" onClick={() => openStation(s.station)}>{s.station}</button></td><td>{s.distance}</td></tr>
                  ))}</tbody>
                </table>
              </>
            )}
          </div>
        </div>

        <div>
          <div className="panel" style={{ marginBottom: 12 }}>
            <h2>CRITICAL RULES (APRIORI)</h2>
            <div className="body">
              {rules.slice(0, 6).map((r, i) => (
                <div className="rule" key={i}>
                  <div>{r.antecedents} → <b>{r.consequents}</b></div>
                  <div>sup {r.support} · conf {r.confidence} · <span className="lift">lift {r.lift}</span></div>
                </div>
              ))}
            </div>
          </div>
          <div className="panel">
            <h2>ANOMALY ALERTS ({alerts.length})</h2>
            <div className="body">
              {alerts.slice(0, 10).map(a => (
                <div className="alert" key={a.station}>
                  <button className="rowbtn" onClick={() => openStation(a.station)}>{a.station}</button>
                  <small>{a.district} · Δ {a.annual_decline?.toFixed(2)} m/yr</small>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <footer>STRATA · SIH25068 · depth convention: larger = deeper = worse · forecast = 30-day linear vs persistence · risk = MLP P(cross 35 m in 90 d), threshold 0.235</footer>
    </>
  );
}
