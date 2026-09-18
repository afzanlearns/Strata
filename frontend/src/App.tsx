import { useEffect, useState } from 'react';
import './index.css';
import { api } from './api';
import type { District, DistrictDetail, StationDetail } from './api';

const LABEL_HINT: Record<string, string> = {
  safe: 'Safe', semi_critical: 'Semi-critical', critical: 'Critical', over_exploited: 'Over-exploited',
};

function Pill({ label }: { label: string }) {
  return <span className={`pill ${label}`}>{LABEL_HINT[label] ?? label}</span>;
}

function TrendChart({ series, forecast }: {
  series: { date: string; depth: number }[];
  forecast: { date: string; actual: number; predicted: number }[];
}) {
  const W = 640, H = 220, P = 36;
  const pts = series.slice(-160);
  const all = [...pts.map(p => p.depth), ...forecast.map(f => f.predicted)];
  if (!pts.length) return <p className="empty">No series data for this station.</p>;
  const lo = Math.min(...all), hi = Math.max(...all), span = hi - lo || 1;
  const X = (i: number, n: number) => P + (i / Math.max(1, n - 1)) * (W - 2 * P);
  const Y = (v: number) => H - P - ((v - lo) / span) * (H - 2 * P);
  const line = (vals: number[]) => vals.map((v, i) => `${X(i, vals.length)},${Y(v)}`).join(' ');
  const fx = (i: number) => X(pts.length - forecast.length + i, pts.length);
  const fline = forecast.map((f, i) => `${fx(i)},${Y(f.predicted)}`).join(' ');
  const last = forecast.length ? forecast[forecast.length - 1].date.slice(0, 10) : '';
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" className="chart" role="img" aria-label="Depth trend">
      <text x={P} y={16} fontSize="11" style={{ fill: 'var(--muted)' }}>
        Depth (m) — larger is deeper · range {lo.toFixed(0)}–{hi.toFixed(0)}
      </text>
      {[0.25, 0.5, 0.75].map(t => (
        <line key={t} x1={P} x2={W - P} y1={P + t * (H - 2 * P)} y2={P + t * (H - 2 * P)} style={{ stroke: 'var(--chart-grid)' }} strokeWidth="1" />
      ))}
      <polyline points={line(pts.map(p => p.depth))} fill="none" style={{ stroke: 'var(--chart-line)' }} strokeWidth="1.75" />
      {forecast.length > 0 && (
        <polyline points={fline} fill="none" style={{ stroke: 'var(--accent)' }} strokeWidth="1.75" strokeDasharray="5 4" />
      )}
      <text x={P} y={H - 8} fontSize="11" style={{ fill: 'var(--muted)' }}>
        Observed <tspan style={{ fill: 'var(--chart-line)' }}>—</tspan> · 30-day forecast <tspan style={{ fill: 'var(--accent)' }}>- -</tspan>
        {last ? ` · through ${last}` : ''}
      </text>
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
  const [theme, setTheme] = useState<string>(() => {
    try {
      const saved = localStorage.getItem('strata-theme');
      if (saved) return saved;
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    } catch { return 'light'; }
  });
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('strata-theme', theme); } catch { /* private mode */ }
  }, [theme]);

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
        <div className="head-row">
          <div>
            <h1>Strata</h1>
            <p className="sub">Groundwater resource evaluation · SIH25068 · Ministry of Jal Shakti · Punjab + Rajasthan DWLR telemetry, 2022–2025</p>
          </div>
          <button className="theme-toggle" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            aria-label="Toggle dark mode">
            {theme === 'dark' ? '○ Light' : '● Dark'}
          </button>
        </div>
        {summary && (
          <p className="meta">
            <strong className="mono">{summary.stations}</strong> stations ·{' '}
            <strong className="mono">{summary.districts}</strong> districts ·{' '}
            <strong className="mono">{summary.anomalies}</strong> anomalies flagged
          </p>
        )}
      </header>
      <div className="layout">
        <div className="panel">
          <h2>Districts</h2>
          <div className="body">
            <select value={stateF} onChange={e => setStateF(e.target.value)} style={{ width: '100%', marginBottom: 10 }}>
              <option value="">All states</option>
              <option value="punjab">Punjab</option>
              <option value="rajasthan">Rajasthan</option>
            </select>
            {districts.map(d => (
              <button key={d.state + d.district} className={`rowbtn${selD?.district === d.district ? ' active' : ''}`}
                onClick={() => setSelD({ state: d.state, district: d.district })}>
                <Pill label={d.label} /> {d.district}{' '}
                <span className="muted mono" style={{ fontSize: 11 }}>{d.n_stations} wells</span>
              </button>
            ))}
          </div>
        </div>

        <div className="panel">
          <h2>{station ? 'Station' : detail ? 'District overview' : 'Overview'}</h2>
          <div className="body">
            {!detail && (
              <p className="empty">Select a district to inspect its groundwater status, then open a station for trend, forecast, crossing risk, and similar wells.</p>
            )}
            {detail && !station && (
              <>
                <h3>{detail.district} <Pill label={detail.label} /></h3>
                <dl className="kv">
                  <dt>Monitoring wells</dt><dd className="mono">{detail.n_stations}</dd>
                  <dt>Median depth</dt><dd><span className="mono">{detail.median_depth?.toFixed(1)} m</span></dd>
                  <dt>Annual change</dt><dd className={detail.annual_decline > 0 ? 'neg' : 'pos'}><span className="mono">{detail.annual_decline?.toFixed(2)} m/yr</span></dd>
                  <dt>Deepening share</dt><dd><span className="mono">{(detail.frac_deepening * 100)?.toFixed(0)}%</span></dd>
                </dl>
                <table>
                  <thead><tr><th>Station</th><th>Depth</th><th>Δ / yr</th><th>Status</th></tr></thead>
                  <tbody>
                    {detail.stations.map(s => (
                      <tr key={s.station}>
                        <td><button className="rowbtn mono" style={{ margin: 0 }} onClick={() => openStation(s.station)}>{s.station}</button></td>
                        <td className="mono">{s.median_depth?.toFixed(1)}</td>
                        <td className={s.annual_decline > 0 ? 'neg mono' : 'pos mono'}>{s.annual_decline?.toFixed(2)}</td>
                        <td>{s.if_flag ? <span className="pill critical">Anomaly</span> : <span className="muted">Cluster {s.kmeans}</span>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </>
            )}
            {station && (
              <>
                <button className="back" onClick={() => setStation(null)}>← Back to {station.district}</button>
                <h3 className="mono" style={{ fontSize: 15 }}>{station.station} <Pill label={station.label} /></h3>
                <dl className="kv">
                  <dt>Median depth</dt><dd><span className="mono">{station.median_depth?.toFixed(1)} m</span></dd>
                  <dt>Annual change</dt><dd className={station.annual_decline > 0 ? 'neg' : 'pos'}><span className="mono">{station.annual_decline?.toFixed(2)} m/yr</span></dd>
                  <dt>Monsoon response</dt><dd><span className="mono">{station.monsoon_delta?.toFixed(2)} m</span> <span className="muted">(negative = recovery)</span></dd>
                  <dt>Behaviour cluster</dt><dd>Archetype {station.kmeans}</dd>
                  <dt>Anomaly screen</dt><dd>{station.if_flag ? <span className="pill critical">Flagged · score <span className="mono">{station.if_score?.toFixed(2)}</span></span> : <span className="muted">No flag</span>}</dd>
                  <dt>90-day crossing risk</dt>
                  <dd><span className={`pill ${station.risk >= 0.235 ? 'risk-high' : 'risk-low'}`}>
                    <span className="mono">{(station.risk * 100).toFixed(1)}%</span> · {station.risk >= 0.235 ? 'Elevated' : 'Low'}</span></dd>
                </dl>
                <TrendChart series={station.series} forecast={station.forecast} />
                <h4>Similar stations</h4>
                <p className="muted" style={{ fontSize: 12, margin: '0 0 8px' }}>Nearest neighbours in behaviour space (Euclidean, standardised features).</p>
                <table>
                  <thead><tr><th>Station</th><th>Distance</th></tr></thead>
                  <tbody>{similar.map(s => (
                    <tr key={s.station}><td><button className="rowbtn mono" style={{ margin: 0 }} onClick={() => openStation(s.station)}>{s.station}</button></td><td className="mono">{s.distance}</td></tr>
                  ))}</tbody>
                </table>
              </>
            )}
          </div>
        </div>

        <div className="side-stack">
          <div className="panel">
            <h2>Association rules</h2>
            <div className="body">
              {rules.slice(0, 6).map((r, i) => (
                <div className="rule" key={i}>
                  <div><span className="mono">{r.antecedents}</span> → <strong>{r.consequents}</strong></div>
                  <div className="metrics">support <b className="mono">{r.support}</b> · confidence <b className="mono">{r.confidence}</b> · lift <b className="mono">{r.lift}</b></div>
                </div>
              ))}
            </div>
          </div>
          <div className="panel">
            <h2>Anomaly alerts <span className="muted mono">{alerts.length}</span></h2>
            <div className="body">
              {alerts.slice(0, 10).map(a => (
                <div className="alert" key={a.station}>
                  <button className="rowbtn mono" style={{ margin: '0 0 2px' }} onClick={() => openStation(a.station)}>{a.station}</button>
                  <small>{a.district} · <span className="mono">{a.annual_decline?.toFixed(2)} m/yr</span></small>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <footer>Strata · SIH25068 · Depth convention: larger means deeper and worse · Forecast: 30-day linear model vs persistence baseline · Risk: P(depth crosses 35 m within 90 days), alert threshold 0.235</footer>
    </>
  );
}
