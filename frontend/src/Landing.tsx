import { useState } from 'react';
import './landing.css';

const FAQ = [
  {
    q: 'What data does STRATA use?',
    a: 'Real-time telemetry from CGWB Deep Water Level Recorders (DWLR) across Punjab and Rajasthan — approximately 802 stations, 2 million rows, spanning September 2022 to December 2025.',
  },
  {
    q: 'Why is "larger depth" worse?',
    a: 'Depth-to-water measures how far below the surface the water table sits. A larger number means the water is deeper — the aquifer is more depleted. The sign convention is locked: larger = deeper = worse.',
  },
  {
    q: 'How does the 30-day forecast work?',
    a: 'A simple linear trend projected forward 30 days, compared against a persistence baseline (yesterday\'s depth = tomorrow\'s). The high R² (0.994) is a "persistence mirage" — water levels change slowly, so yesterday\'s value is already a strong predictor.',
  },
  {
    q: 'What does the crossing-risk percentage mean?',
    a: 'It\'s the probability that a station\'s depth will cross 35 metres within 90 days, estimated by an MLP neural network. The alert threshold is 0.235 — above that, the badge turns red ("Elevated").',
  },
  {
    q: 'What are quarantine flags?',
    a: 'Readings flagged as sensor-level issues: `mad_outlier` (statistical outlier), `nonphysical` (impossible value), `datum_shift` (abrupt jump), `gap` (missing data). Rows are never deleted — the `qflag` column makes them queryable so you can still see what was flagged and why.',
  },
  {
    q: 'What do the association rules show?',
    a: 'How districts co-occur in the same groundwater category (Safe / Semi-critical / Critical / Over-exploited) across Kharif and Rabi seasons. Lift > 1 means the pattern is stronger than random chance — useful for regional planning.',
  },
  {
    q: 'How are the ML techniques validated?',
    a: 'Classification (kNN, Decision Tree, Naive Bayes) uses train/test split with macro-F1 scoring. Regression compares against a persistence baseline. Clustering uses silhouette score and Adjusted Rand Index against hierarchical clustering. Association rules are filtered by lift > 1.',
  },
  {
    q: 'Can I switch between light and dark mode?',
    a: 'Yes — the toggle is in the top-right corner of the dashboard. Your preference is saved in localStorage and respects your OS setting on first visit.',
  },
];

function WireDiagram() {
  return (
    <svg viewBox="0 0 700 120" className="wire-diagram" aria-label="Data flow diagram">
      {[
        { x: 20, label: 'CGWB\nSensors', color: 'var(--green-mid)' },
        { x: 180, label: 'Preprocessing\n& QA', color: 'var(--green-mid)' },
        { x: 340, label: 'ML Pipeline\nForecasting', color: 'var(--accent)' },
        { x: 500, label: 'FastAPI\nBackend', color: 'var(--accent)' },
        { x: 640, label: 'React\nDashboard', color: 'var(--green-mid)' },
      ].map((b, i, arr) => (
        <g key={i}>
          {i < arr.length - 1 && (
            <line x1={b.x + 50} y1={60} x2={arr[i + 1].x - 10} y2={60}
              stroke="var(--border)" strokeWidth="1.5" strokeDasharray="4 3" />
          )}
          <rect x={b.x - 40} y={25} width={100} height={70} rx={6}
            fill="var(--panel)" stroke={b.color} strokeWidth="1.5" />
          {b.label.split('\n').map((line, li) => (
            <text key={li} x={b.x + 10} y={58 + li * 16}
              textAnchor="middle" fontSize="11.5" fontWeight="500"
              style={{ fill: 'var(--ink)' }}>{line}</text>
          ))}
        </g>
      ))}
    </svg>
  );
}

function DashboardMockup() {
  return (
    <svg viewBox="0 0 520 300" className="mockup" aria-label="Dashboard preview">
      <rect width="520" height="300" rx="6" fill="var(--panel)" stroke="var(--border)" strokeWidth="1" />
      <text x="20" y="28" fontSize="13" fontWeight="600" style={{ fill: 'var(--ink)' }}>Strata</text>
      <text x="20" y="44" fontSize="9" style={{ fill: 'var(--muted)' }}>Groundwater levels across Punjab and Rajasthan</text>
      <rect x="20" y="60" width="140" height="220" rx="4" fill="var(--faint)" stroke="var(--border-soft)" strokeWidth="0.75" />
      <text x="30" y="78" fontSize="9" fontWeight="500" style={{ fill: 'var(--muted)' }}>Districts</text>
      {[0, 1, 2, 3, 4].map(i => (
        <rect key={i} x="28" y={90 + i * 28} width={120} height={20} rx={3}
          fill={i === 1 ? 'var(--accent-soft)' : 'var(--panel)'} stroke="var(--border-soft)" strokeWidth="0.5" />
      ))}
      <text x="38" y="104" fontSize="8" style={{ fill: 'var(--ink)' }}>Ludhiana</text>
      <text x="38" y="132" fontSize="8" fontWeight="600" style={{ fill: 'var(--accent)' }}>Patiala</text>
      <text x="38" y="160" fontSize="8" style={{ fill: 'var(--ink)' }}>Amritsar</text>
      <text x="38" y="188" fontSize="8" style={{ fill: 'var(--ink)' }}>Jalandhar</text>
      <text x="38" y="216" fontSize="8" style={{ fill: 'var(--ink)' }}>Bathinda</text>
      <rect x="175" y="60" width="210" height="220" rx="4" fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.75" />
      <text x="185" y="78" fontSize="9" fontWeight="500" style={{ fill: 'var(--muted)' }}>Station overview</text>
      <text x="185" y="100" fontSize="11" fontWeight="600" style={{ fill: 'var(--ink)' }}>Patiala — PB-PTL-0042</text>
      <polyline points="185,160 210,155 235,158 260,148 285,152 310,145 335,140 360,135 380,130"
        fill="none" stroke="var(--chart-line)" strokeWidth="1.5" />
      <polyline points="360,130 375,126 385,122"
        fill="none" stroke="var(--accent)" strokeWidth="1.5" strokeDasharray="3 2" />
      <rect x="185" y="190" width="80" height="18" rx="9" fill="var(--crit-bg)" />
      <text x="205" y="203" fontSize="8" fontWeight="500" style={{ fill: 'var(--crit-tx)' }}>72.3% Elevated</text>
      <text x="185" y="230" fontSize="8" style={{ fill: 'var(--muted)' }}>Depth (m) — larger is deeper</text>
      <text x="185" y="260" fontSize="8" style={{ fill: 'var(--muted)' }}>Observed — · Forecast - -</text>
      <rect x="400" y="60" width="100" height="220" rx="4" fill="var(--faint)" stroke="var(--border-soft)" strokeWidth="0.75" />
      <text x="410" y="78" fontSize="9" fontWeight="500" style={{ fill: 'var(--muted)' }}>Alerts</text>
      {[0, 1, 2].map(i => (
        <rect key={i} x="408" y={90 + i * 40} width={84} height={32} rx={3}
          fill="var(--panel)" stroke="var(--border-soft)" strokeWidth="0.5" />
      ))}
      <text x="415" y="106" fontSize="7" style={{ fill: 'var(--ink)' }}>PB-AMR-0018</text>
      <text x="415" y="116" fontSize="6.5" style={{ fill: 'var(--muted)' }}>Amritsar · 1.2 m/yr</text>
      <text x="415" y="146" fontSize="7" style={{ fill: 'var(--ink)' }}>RJ-JAI-0007</text>
      <text x="415" y="156" fontSize="6.5" style={{ fill: 'var(--muted)' }}>Jaipur · 0.8 m/yr</text>
      <text x="415" y="186" fontSize="7" style={{ fill: 'var(--ink)' }}>RJ-JDR-0031</text>
      <text x="415" y="196" fontSize="6.5" style={{ fill: 'var(--muted)' }}>Jodhpur · 2.1 m/yr</text>
    </svg>
  );
}

export default function Landing({ onOpen }: { onOpen: () => void }) {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  return (
    <div className="landing">
      {/* ── Hero ── */}
      <section className="hero">
        <div className="hero-inner">
          <span className="hero-badge">SIH25068 · Ministry of Jal Shakti</span>
          <h1>Strata</h1>
          <p className="hero-sub">
            Real-time groundwater monitoring for Punjab and Rajasthan.
            <br />802 stations, 2022–2025 telemetry, ML-powered forecasting.
          </p>
          <button className="cta" onClick={onOpen}>Open dashboard →</button>
          <p className="hero-note">Depth convention: larger = deeper = worse</p>
        </div>
        <div className="hero-visual">
          <DashboardMockup />
        </div>
      </section>

      {/* ── About ── */}
      <section className="about" id="about">
        <div className="section-inner">
          <h2>About the project</h2>
          <p>
            STRATA is a groundwater resource evaluation system built for the Smart India
            Hackathon. It ingests real telemetry from CGWB Deep Water Level Recorders
            across Punjab and Rajasthan, unifies noisy sensor data, and surfaces
            district-level groundwater status through machine learning — classification,
            forecasting, anomaly detection, and association mining — in a single
            browser-based dashboard.
          </p>
          <p>
            The goal: give water-resource managers a clear, immediate picture of
            which districts are trending toward over-exploitation, which stations
            are behaving abnormally, and what the next 30 days look like — without
            digging through spreadsheets.
          </p>
        </div>
      </section>

      {/* ── Pipeline ── */}
      <section className="pipeline" id="pipeline">
        <div className="section-inner">
          <h2>How it works</h2>
          <p className="section-lead">Data flows from field sensors through the ML pipeline to your screen.</p>
          <WireDiagram />
        </div>
      </section>

      {/* ── Features ── */}
      <section className="features" id="features">
        <div className="section-inner">
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
      <section className="demo" id="demo">
        <div className="section-inner">
          <h2>How to use it</h2>
          <div className="demo-steps">
            {[
              { step: '1', title: 'Pick a district', text: 'Use the left panel to filter by state, then click a district. The centre panel loads its overview — station count, median depth, annual decline.' },
              { step: '2', title: 'Inspect a station', text: 'Click any station row. The centre panel shows its depth trend chart, 30-day forecast (dashed blue), crossing-risk badge, and behaviour cluster.' },
              { step: '3', title: 'Check anomalies', text: 'The right sidebar lists anomaly alerts — stations flagged by Isolation Forest. Click one to jump to its detail view.' },
              { step: '4', title: 'Read the rules', text: 'Association rules show how districts co-occur in groundwater categories. Lift > 1 means the pattern is stronger than random.' },
            ].map((d, i) => (
              <div className="demo-step" key={i}>
                <div className="demo-num">{d.step}</div>
                <div>
                  <h3>{d.title}</h3>
                  <p>{d.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FAQ ── */}
      <section className="faq-section" id="faq">
        <div className="section-inner">
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
