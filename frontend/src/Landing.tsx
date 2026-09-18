import { useState } from 'react';
import './landing.css';

const FAQ = [
  {
    q: 'What data does STRATA use?',
    a: 'Real-time telemetry from CGWB Deep Water Level Recorders across Punjab and Rajasthan — 802 stations, ~2 million rows, September 2022 to December 2025.',
  },
  {
    q: 'Why is "larger depth" worse?',
    a: 'Depth-to-water measures how far below the surface the water table sits. A larger number means the water is deeper — the aquifer is more depleted. Convention: larger = deeper = worse.',
  },
  {
    q: 'How does the 30-day forecast work?',
    a: 'A linear trend projected forward 30 days, compared against a persistence baseline. The high R² (0.994) is a "persistence mirage" — water levels change slowly, so yesterday\'s value is already a strong predictor.',
  },
  {
    q: 'What does the crossing-risk percentage mean?',
    a: 'The probability that a station\'s depth will cross 35 metres within 90 days, estimated by an MLP neural network. Alert threshold: 0.235 — above that, the badge turns red ("Elevated").',
  },
  {
    q: 'What are quarantine flags?',
    a: 'Sensor-level issue flags: mad_outlier, nonphysical, datum_shift, gap. Rows are never deleted — the qflag column makes them queryable so you can see what was flagged and why.',
  },
];

function PipelineDiagram() {
  const stages = [
    { label: 'CGWB Sensors', sub: 'DWLR telemetry', color: 'var(--green-mid)', icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--green-mid)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2v6m0 0l-3-3m3 3l3-3"/><rect x="4" y="10" width="16" height="10" rx="2"/><line x1="8" y1="14" x2="8" y2="16"/><line x1="12" y1="14" x2="12" y2="16"/><line x1="16" y1="14" x2="16" y2="16"/>
      </svg>
    )},
    { label: 'Preprocessing', sub: 'Sign unify · QA · Quarantine', color: 'var(--green-mid)', icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--green-mid)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/>
        <circle cx="12" cy="7" r="3"/><circle cx="18" cy="2" r="2"/><circle cx="6" cy="14" r="2"/>
      </svg>
    )},
    { label: 'ML Pipeline', sub: 'Forecast · Classify · Cluster', color: 'var(--accent)', icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/>
      </svg>
    )},
    { label: 'FastAPI', sub: 'SQLite / MySQL', color: 'var(--accent)', icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
      </svg>
    )},
    { label: 'Dashboard', sub: 'React + TypeScript', color: 'var(--green-mid)', icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--green-mid)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
      </svg>
    )},
  ];
  return (
    <div className="pipeline-row">
      {stages.map((s, i) => (
        <div key={i} className="pipeline-stage">
          <div className="pipeline-box" style={{ borderColor: s.color }}>
            <span className="pipeline-icon">{s.icon}</span>
            <span className="pipeline-label">{s.label}</span>
            <span className="pipeline-sub">{s.sub}</span>
          </div>
          {i < stages.length - 1 && (
            <svg className="pipeline-arrow" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--green-mid)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="4" y1="12" x2="20" y2="12"/><polyline points="14 6 20 12 14 18"/>
            </svg>
          )}
        </div>
      ))}
    </div>
  );
}

function StepMockup({ step }: { step: number }) {
  if (step === 1) return (
    <svg viewBox="0 0 240 140" className="step-mock">
      <rect width="240" height="140" rx="4" fill="var(--panel)" stroke="var(--border)" strokeWidth="0.75" />
      <rect x="8" y="8" width="72" height="124" rx="3" fill="var(--faint)" stroke="var(--border-soft)" strokeWidth="0.5" />
      <text x="14" y="22" fontSize="7" fontWeight="500" style={{ fill: 'var(--muted)' }}>Districts</text>
      <rect x="12" y="28" width="64" height="14" rx="2" fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.4" />
      <text x="16" y="38" fontSize="6" style={{ fill: 'var(--ink)' }}>Ludhiana</text>
      <rect x="12" y="46" width="64" height="14" rx="2" fill="var(--accent-soft)" stroke="var(--accent)" strokeWidth="0.5" />
      <text x="16" y="56" fontSize="6" fontWeight="600" style={{ fill: 'var(--accent)' }}>Patiala</text>
      <rect x="12" y="64" width="64" height="14" rx="2" fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.4" />
      <text x="16" y="74" fontSize="6" style={{ fill: 'var(--ink)' }}>Amritsar</text>
      <rect x="12" y="82" width="64" height="14" rx="2" fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.4" />
      <text x="16" y="92" fontSize="6" style={{ fill: 'var(--ink)' }}>Jalandhar</text>
      <rect x="88" y="8" width="144" height="124" rx="3" fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.5" />
      <text x="94" y="22" fontSize="7" fontWeight="500" style={{ fill: 'var(--muted)' }}>District overview</text>
      <text x="94" y="38" fontSize="8" fontWeight="600" style={{ fill: 'var(--ink)' }}>Patiala</text>
      <rect x="120" y="32" width="36" height="10" rx="5" fill="var(--semi-bg)" />
      <text x="130" y="40" fontSize="5" fontWeight="500" style={{ fill: 'var(--semi-tx)' }}>Semi-crit</text>
      <text x="94" y="54" fontSize="6" style={{ fill: 'var(--muted)' }}>Wells</text>
      <text x="120" y="54" fontSize="6" fontWeight="600" style={{ fill: 'var(--ink)' }}>42</text>
      <text x="94" y="66" fontSize="6" style={{ fill: 'var(--muted)' }}>Median</text>
      <text x="120" y="66" fontSize="6" fontWeight="600" style={{ fill: 'var(--ink)' }}>18.4 m</text>
      <text x="94" y="78" fontSize="6" style={{ fill: 'var(--muted)' }}>Δ / yr</text>
      <text x="120" y="78" fontSize="6" fontWeight="600" style={{ fill: 'var(--crit-tx)' }}>+0.82</text>
    </svg>
  );
  if (step === 2) return (
    <svg viewBox="0 0 240 140" className="step-mock">
      <rect width="240" height="140" rx="4" fill="var(--panel)" stroke="var(--border)" strokeWidth="0.75" />
      <text x="12" y="18" fontSize="7" fontWeight="600" style={{ fill: 'var(--ink)' }}>PB-PTL-0042</text>
      <rect x="140" y="10" width="52" height="14" rx="7" fill="var(--crit-bg)" />
      <text x="152" y="20" fontSize="6" fontWeight="500" style={{ fill: 'var(--crit-tx)' }}>72.3%</text>
      <polyline points="12,60 36,55 60,58 84,48 108,52 132,45 156,40 180,38 200,35 220,32"
        fill="none" stroke="var(--chart-line)" strokeWidth="1.2" />
      <polyline points="200,35 215,30 228,27"
        fill="none" stroke="var(--accent)" strokeWidth="1.2" strokeDasharray="3 2" />
      <text x="12" y="80" fontSize="6" style={{ fill: 'var(--muted)' }}>Depth (m)</text>
      <line x1="12" y1="88" x2="228" y2="88" stroke="var(--border-soft)" strokeWidth="0.4" />
      <text x="12" y="98" fontSize="6" style={{ fill: 'var(--chart-line)' }}>— observed</text>
      <text x="80" y="98" fontSize="6" style={{ fill: 'var(--accent)' }}>- - forecast</text>
      <text x="12" y="114" fontSize="6" style={{ fill: 'var(--muted)' }}>Median depth</text>
      <text x="80" y="114" fontSize="6" fontWeight="600" style={{ fill: 'var(--ink)' }}>18.4 m</text>
      <text x="12" y="126" fontSize="6" style={{ fill: 'var(--muted)' }}>Annual change</text>
      <text x="80" y="126" fontSize="6" fontWeight="600" style={{ fill: 'var(--crit-tx)' }}>+0.82 m/yr</text>
    </svg>
  );
  if (step === 3) return (
    <svg viewBox="0 0 240 140" className="step-mock">
      <rect width="240" height="140" rx="4" fill="var(--panel)" stroke="var(--border)" strokeWidth="0.75" />
      <text x="12" y="18" fontSize="7" fontWeight="500" style={{ fill: 'var(--muted)' }}>Anomaly alerts</text>
      <rect x="12" y="24" width="216" height="30" rx="3" fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.5" />
      <text x="18" y="38" fontSize="6" fontWeight="600" style={{ fill: 'var(--ink)' }}>PB-AMR-0018</text>
      <text x="18" y="48" fontSize="5.5" style={{ fill: 'var(--muted)' }}>Amritsar · 1.2 m/yr</text>
      <rect x="170" y="30" width="48" height="12" rx="6" fill="var(--crit-bg)" />
      <text x="180" y="39" fontSize="5" fontWeight="500" style={{ fill: 'var(--crit-tx)' }}>Flagged</text>
      <rect x="12" y="58" width="216" height="30" rx="3" fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.5" />
      <text x="18" y="72" fontSize="6" fontWeight="600" style={{ fill: 'var(--ink)' }}>RJ-JAI-0007</text>
      <text x="18" y="82" fontSize="5.5" style={{ fill: 'var(--muted)' }}>Jaipur · 0.8 m/yr</text>
      <rect x="170" y="64" width="48" height="12" rx="6" fill="var(--crit-bg)" />
      <text x="180" y="73" fontSize="5" fontWeight="500" style={{ fill: 'var(--crit-tx)' }}>Flagged</text>
      <rect x="12" y="92" width="216" height="30" rx="3" fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.5" />
      <text x="18" y="106" fontSize="6" fontWeight="600" style={{ fill: 'var(--ink)' }}>RJ-JDR-0031</text>
      <text x="18" y="116" fontSize="5.5" style={{ fill: 'var(--muted)' }}>Jodhpur · 2.1 m/yr</text>
      <rect x="170" y="98" width="48" height="12" rx="6" fill="var(--crit-bg)" />
      <text x="180" y="107" fontSize="5" fontWeight="500" style={{ fill: 'var(--crit-tx)' }}>Flagged</text>
    </svg>
  );
  return (
    <svg viewBox="0 0 240 140" className="step-mock">
      <rect width="240" height="140" rx="4" fill="var(--panel)" stroke="var(--border)" strokeWidth="0.75" />
      <text x="12" y="18" fontSize="7" fontWeight="500" style={{ fill: 'var(--muted)' }}>Association rules</text>
      <rect x="12" y="24" width="216" height="32" rx="3" fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.5" />
      <text x="18" y="36" fontSize="6" style={{ fill: 'var(--ink)' }}>
        <tspan fontWeight="600">Patiala=SC</tspan> → <tspan fontWeight="600">Ludhiana=C</tspan>
      </text>
      <text x="18" y="48" fontSize="5.5" style={{ fill: 'var(--muted)' }}>sup 0.12 · conf 0.78 · lift 2.31</text>
      <rect x="12" y="60" width="216" height="32" rx="3" fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.5" />
      <text x="18" y="72" fontSize="6" style={{ fill: 'var(--ink)' }}>
        <tspan fontWeight="600">Amritsar=OE</tspan> → <tspan fontWeight="600">Jalandhar=SC</tspan>
      </text>
      <text x="18" y="84" fontSize="5.5" style={{ fill: 'var(--muted)' }}>sup 0.09 · conf 0.65 · lift 1.84</text>
      <rect x="12" y="96" width="216" height="32" rx="3" fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.5" />
      <text x="18" y="108" fontSize="6" style={{ fill: 'var(--ink)' }}>
        <tspan fontWeight="600">Bathinda=C</tspan> → <tspan fontWeight="600">Moga=C</tspan>
      </text>
      <text x="18" y="120" fontSize="5.5" style={{ fill: 'var(--muted)' }}>sup 0.15 · conf 0.71 · lift 1.96</text>
    </svg>
  );
}

function DashboardMini() {
  return (
    <svg viewBox="0 0 480 260" className="hero-mock" aria-label="Dashboard preview">
      <defs>
        <filter id="shadow" x="-4%" y="-4%" width="108%" height="112%">
          <feDropShadow dx="0" dy="2" stdDeviation="6" floodOpacity="0.08" />
        </filter>
      </defs>
      <rect width="480" height="260" rx="8" fill="var(--panel)" filter="url(#shadow)" stroke="var(--border)" strokeWidth="0.75" />
      <text x="20" y="26" fontSize="14" fontWeight="700" style={{ fill: 'var(--ink)' }}>Strata</text>
      <text x="20" y="40" fontSize="8" style={{ fill: 'var(--muted)' }}>Groundwater levels across Punjab and Rajasthan</text>
      <rect x="16" y="52" width="120" height="196" rx="4" fill="var(--faint)" stroke="var(--border-soft)" strokeWidth="0.5" />
      <text x="24" y="68" fontSize="8" fontWeight="500" style={{ fill: 'var(--muted)' }}>Districts</text>
      {['Ludhiana', 'Patiala', 'Amritsar', 'Jalandhar', 'Bathinda'].map((d, i) => (
        <g key={d}>
          <rect x="22" y={76 + i * 26} width={104} height={18} rx={3}
            fill={i === 1 ? 'var(--accent-soft)' : 'var(--panel)'} stroke={i === 1 ? 'var(--accent)' : 'var(--border-soft)'} strokeWidth={i === 1 ? '0.75' : '0.4'} />
          <text x="28" y={88 + i * 26} fontSize="7" fontWeight={i === 1 ? '600' : '400'}
            style={{ fill: i === 1 ? 'var(--accent)' : 'var(--ink)' }}>{d}</text>
        </g>
      ))}
      <rect x="148" y="52" width="196" height="196" rx="4" fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.5" />
      <text x="158" y="68" fontSize="8" fontWeight="500" style={{ fill: 'var(--muted)' }}>Station overview</text>
      <text x="158" y="86" fontSize="10" fontWeight="600" style={{ fill: 'var(--ink)' }}>Patiala — PB-PTL-0042</text>
      <polyline points="158,130 178,126 198,128 218,120 238,122 258,118 278,114 298,110 318,106 334,102"
        fill="none" stroke="var(--chart-line)" strokeWidth="1.5" />
      <polyline points="318,106 330,100 340,96"
        fill="none" stroke="var(--accent)" strokeWidth="1.5" strokeDasharray="3 2" />
      <rect x="158" y="150" width="68" height="16" rx="8" fill="var(--crit-bg)" />
      <text x="170" y="161" fontSize="7" fontWeight="500" style={{ fill: 'var(--crit-tx)' }}>72.3%</text>
      <text x="158" y="180" fontSize="7" style={{ fill: 'var(--muted)' }}>Depth (m) — larger is deeper</text>
      <text x="158" y="194" fontSize="7" style={{ fill: 'var(--muted)' }}>Observed — · Forecast - -</text>
      <text x="158" y="220" fontSize="7" style={{ fill: 'var(--muted)' }}>Median depth</text>
      <text x="220" y="220" fontSize="7" fontWeight="600" style={{ fill: 'var(--ink)' }}>18.4 m</text>
      <rect x="356" y="52" width="108" height="196" rx="4" fill="var(--faint)" stroke="var(--border-soft)" strokeWidth="0.5" />
      <text x="364" y="68" fontSize="8" fontWeight="500" style={{ fill: 'var(--muted)' }}>Alerts</text>
      {['PB-AMR-0018', 'RJ-JAI-0007', 'RJ-JDR-0031'].map((s, i) => (
        <g key={s}>
          <rect x="362" y={76 + i * 38} width={96} height={30} rx={3} fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.4" />
          <text x="368" y={88 + i * 38} fontSize="6" fontWeight="600" style={{ fill: 'var(--ink)' }}>{s}</text>
          <text x="368" y={98 + i * 38} fontSize="5.5" style={{ fill: 'var(--muted)' }}>{['Amritsar', 'Jaipur', 'Jodhpur'][i]}</text>
        </g>
      ))}
    </svg>
  );
}

export default function Landing({ onOpen, theme, setTheme }: { onOpen: () => void; theme: string; setTheme: (t: string) => void }) {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  return (
    <div className="landing">
      {/* ── Nav ── */}
      <nav className="land-nav">
        <span className="land-nav-title">Strata</span>
        <div className="land-nav-right">
          <button className="theme-toggle" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            aria-label="Toggle dark mode">
            {theme === 'dark' ? '○ Light' : '● Dark'}
          </button>
        </div>
      </nav>
      {/* ── Hero ── */}
      <section className="sec sec-hero">
        <div className="sec-content hero-grid">
          <div className="hero-text">
            <span className="hero-badge">SIH25068 · Ministry of Jal Shakti</span>
            <h1>Strata</h1>
            <p className="hero-sub">
              Real-time groundwater monitoring for Punjab and Rajasthan. 802 stations, 2022–2025 telemetry, ML-powered forecasting.
            </p>
            <button className="cta" onClick={onOpen}>Open dashboard →</button>
            <p className="hero-note">Depth convention: larger = deeper = worse</p>
          </div>
          <div className="hero-visual">
            <DashboardMini />
          </div>
        </div>
      </section>

      {/* ── About ── */}
      <section className="sec sec-about">
        <div className="sec-content about-grid">
          <div className="about-text">
            <h2>About the project</h2>
            <p>
              STRATA is a groundwater resource evaluation system built for the Smart India
              Hackathon. It ingests real telemetry from CGWB Deep Water Level Recorders
              across Punjab and Rajasthan, unifies noisy sensor data, and surfaces
              district-level groundwater status through machine learning.
            </p>
            <p>
              The goal: give water-resource managers a clear, immediate picture of
              which districts are trending toward over-exploitation, which stations
              are behaving abnormally, and what the next 30 days look like.
            </p>
          </div>
          <div className="about-stats">
            <div className="stat-card">
              <span className="stat-num">802</span>
              <span className="stat-label">DWLR stations</span>
            </div>
            <div className="stat-card">
              <span className="stat-num">~2M</span>
              <span className="stat-label">rows of telemetry</span>
            </div>
            <div className="stat-card">
              <span className="stat-num">2</span>
              <span className="stat-label">states covered</span>
            </div>
            <div className="stat-card">
              <span className="stat-num">4</span>
              <span className="stat-label">ML techniques</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── Pipeline ── */}
      <section className="sec sec-pipeline">
        <div className="sec-content">
          <h2>How it works</h2>
          <p className="section-lead">Data flows from field sensors through the ML pipeline to your screen.</p>
          <PipelineDiagram />
        </div>
      </section>

      {/* ── Features ── */}
      <section className="sec sec-features">
        <div className="sec-content">
          <h2>Features</h2>
          <div className="feature-grid">
            {[
              { title: 'Real-time tracking', desc: 'Ingests raw DWLR telemetry, unifies sign conventions, flags bad readings without deleting data.' },
              { title: '30-day forecast', desc: 'Linear trend projection with persistence baseline comparison for each station.' },
              { title: 'Crossing risk', desc: 'MLP neural network estimates P(depth crosses 35 m in 90 days). Alert threshold: 0.235.' },
              { title: 'Anomaly detection', desc: 'Isolation Forest catches unusual patterns — 63% independent of sensor-level quarantine flags.' },
              { title: 'Association mining', desc: 'Apriori algorithm finds how districts co-occur in groundwater categories across seasons.' },
              { title: 'Behaviour clustering', desc: 'k-means groups stations by depth patterns. DBSCAN + PCA for visual exploration.' },
            ].map((f, i) => (
              <div className="feature-card" key={i}>
                <div className="feature-num">{String(i + 1).padStart(2, '0')}</div>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Demo ── */}
      <section className="sec sec-demo">
        <div className="sec-content">
          <h2>How to use it</h2>
          <div className="demo-grid">
            {[
              { step: 1, title: 'Pick a district', text: 'Filter by state in the left panel, then click a district. The centre panel loads its overview — station count, median depth, annual decline.' },
              { step: 2, title: 'Inspect a station', text: 'Click any station row. The centre panel shows its depth trend chart, 30-day forecast (dashed blue), crossing-risk badge, and behaviour cluster.' },
              { step: 3, title: 'Check anomalies', text: 'The right sidebar lists anomaly alerts — stations flagged by Isolation Forest. Click one to jump to its detail view.' },
              { step: 4, title: 'Read the rules', text: 'Association rules show how districts co-occur in groundwater categories. Lift > 1 means the pattern is stronger than random.' },
            ].map((d) => (
              <div className="demo-card" key={d.step}>
                <div className="demo-mock"><StepMockup step={d.step} /></div>
                <div className="demo-info">
                  <div className="demo-num">{d.step}</div>
                  <h3>{d.title}</h3>
                  <p>{d.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FAQ ── */}
      <section className="sec sec-faq">
        <div className="sec-content">
          <h2>Frequently asked questions</h2>
          <div className="faq-list">
            {FAQ.map((f, i) => (
              <div className={`faq-item${openFaq === i ? ' open' : ''}`} key={i}>
                <button className="faq-q" onClick={() => setOpenFaq(openFaq === i ? null : i)}>
                  <span>{f.q}</span>
                  <span className="faq-icon">{openFaq === i ? '−' : '+'}</span>
                </button>
                {openFaq === i && <p className="faq-a">{f.a}</p>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="site-footer">
        <div className="footer-inner">
          <span>Strata · SIH25068</span>
          <span>Depth convention: larger = deeper = worse</span>
          <span>Forecast: 30-day linear · Risk threshold: 0.235</span>
        </div>
      </footer>
    </div>
  );
}
