export interface Summary {
  stations: number; districts: number; anomalies: number; rules: number;
  labels: Record<string, number>;
}
export interface District {
  state: string; district: string; label: string; n_stations: number;
  median_depth: number; annual_decline: number; frac_deepening: number;
}
export interface StationRow {
  station: string; median_depth: number; annual_decline: number;
  label: string; kmeans: number; if_flag: boolean;
}
export interface DistrictDetail extends District { stations: StationRow[]; }
export interface StationDetail {
  station: string; state: string; district: string; label: string;
  median_depth: number; annual_decline: number; monsoon_delta: number;
  volatility: number; kmeans: number; if_flag: boolean; if_score: number;
  forecast: { date: string; actual: number; predicted: number }[];
  risk: number;
  series: { date: string; depth: number }[];
}
export interface Rule {
  antecedents: string; consequents: string;
  support: number; confidence: number; lift: number;
}
export interface Similar { station: string; distance: number; }
export interface Alert {
  station: string; state: string; district: string;
  if_score: number; annual_decline: number;
}

async function get<T>(path: string): Promise<T> {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json() as Promise<T>;
}

export const api = {
  summary: () => get<Summary>('/api/summary'),
  districts: (state?: string) =>
    get<District[]>(`/api/districts${state ? `?state=${state}` : ''}`),
  district: (state: string, district: string) =>
    get<DistrictDetail>(`/api/districts/${state}/${encodeURIComponent(district)}`),
  station: (name: string) => get<StationDetail>(`/api/stations/${encodeURIComponent(name)}`),
  similar: (name: string) =>
    get<Similar[]>(`/api/stations/${encodeURIComponent(name)}/similar`),
  rules: () => get<Rule[]>('/api/rules?limit=12'),
  alerts: () => get<Alert[]>('/api/alerts'),
};
