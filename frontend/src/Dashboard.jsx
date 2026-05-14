import { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import "./Dashboard.css";

const COLORS = [
  "#6366f1",
  "#22c55e",
  "#06b6d4",
  "#f59e0b",
  "#ef4444",
  "#a855f7",
  "#14b8a6",
  "#eab308",
];

const formatCompact = (n) =>
  new Intl.NumberFormat("en", { notation: "compact" }).format(n || 0);

function DataTable({ title, rows }) {
  return (
    <div className="tableCard">
      <div className="cardTitle">{title}</div>
      <div className="tableWrap">
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th style={{ textAlign: "right" }}>Count</th>
            </tr>
          </thead>
          <tbody>
            {rows?.length ? (
              rows.map((r, i) => (
                <tr key={i}>
                  <td>{r.name}</td>
                  <td style={{ textAlign: "right" }}>{r.count}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="2" style={{ color: "rgba(234,242,255,.65)" }}>
                  No data
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [cityWise, setCityWise] = useState([]);
  const [categoryWise, setCategoryWise] = useState([]);
  const [sourceWise, setSourceWise] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError("");

        const [c1, c2, c3] = await Promise.all([
          fetch("http://127.0.0.1:8000/api/dashboard/city-wise").then((r) =>
            r.json()
          ),
          fetch("http://127.0.0.1:8000/api/dashboard/category-wise").then((r) =>
            r.json()
          ),
          fetch("http://127.0.0.1:8000/api/dashboard/source-wise").then((r) =>
            r.json()
          ),
        ]);
	setCityWise((c1 || []).filter((x) => x?.name && x.name !== "Unknown").slice(0, 10));
        setCategoryWise((c2 || []).slice(0, 10));
        setSourceWise(c3 || []);
      } catch (e) {
        setError(String(e?.message || e));
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const total = useMemo(
    () => sourceWise.reduce((acc, x) => acc + (x.count || 0), 0),
    [sourceWise]
  );

  // KPI improvements: skip "Unknown" for Top City
  const topCity = useMemo(
    () => (cityWise || []).find((x) => x?.name && x.name !== "Unknown"),
    [cityWise]
  );

  const topCategory = categoryWise?.[0];
  const topSource = sourceWise?.[0];

  return (
    <div className="container">
      <div className="header">
        <div className="title">Business Listings Dashboard</div>
        <p className="subtitle">
          MySQL + FastAPI + React (Recharts) — Top 10 for city/category.
        </p>
      </div>

      {error ? (
        <div
          style={{
            background: "rgba(239,68,68,.12)",
            border: "1px solid rgba(239,68,68,.25)",
            padding: 12,
            borderRadius: 14,
            marginBottom: 14,
          }}
        >
          Failed to load dashboard data: {error}
        </div>
      ) : null}

      <div className="kpis">
        <div className="kpi">
          <div className="kpiLabel">Total Listings</div>
          <div className="kpiValue">{loading ? "…" : formatCompact(total)}</div>
          <div className="kpiHint">Across all sources</div>
        </div>

        <div className="kpi">
          <div className="kpiLabel">Top City</div>
          <div className="kpiValue">{loading ? "…" : topCity?.name || "—"}</div>
          <div className="kpiHint">
            {loading
              ? "Loading…"
              : topCity
              ? `${formatCompact(topCity.count)} listings`
              : "No data"}
          </div>
        </div>

        <div className="kpi">
          <div className="kpiLabel">Top Category</div>
          <div className="kpiValue">
            {loading ? "…" : topCategory?.name || "—"}
          </div>
          <div className="kpiHint">
            {loading
              ? "Loading…"
              : topCategory
              ? `${formatCompact(topCategory.count)} listings`
              : "No data"}
          </div>
        </div>

        <div className="kpi">
          <div className="kpiLabel">Top Source</div>
          <div className="kpiValue">
            {loading ? "…" : topSource?.name || "—"}
          </div>
          <div className="kpiHint">
            {loading
              ? "Loading…"
              : topSource
              ? `${formatCompact(topSource.count)} listings`
              : "No data"}
          </div>
        </div>
      </div>

      <div className="grid">
        <div className="card">
          <div className="cardTitle">City-wise business count (Top 10)</div>
          <div className="chartWrap">
            <ResponsiveContainer>
              <BarChart
                data={cityWise}
                margin={{ top: 10, right: 14, left: 0, bottom: 26 }}
              >
                <CartesianGrid
                  stroke="rgba(255,255,255,.08)"
                  strokeDasharray="3 3"
                />
               <XAxis
  		dataKey="name"
  		interval={0}                
 		tickFormatter={(v) => (v.length > 10 ? v.slice(0, 10) + "…" : v)}
  		angle={-25}
  		textAnchor="end"
 		height={60}
  		tick={{ fill: "rgba(234,242,255,.8)", fontSize: 12 }}/>
                <YAxis
                  tick={{ fill: "rgba(234,242,255,.75)", fontSize: 12 }}
                />
                <Tooltip
                  contentStyle={{
                    background: "#0b1628",
                    border: "1px solid rgba(255,255,255,.10)",
                    borderRadius: 12,
                  }}
                  labelStyle={{ color: "rgba(234,242,255,.85)" }}
                />
                <Bar dataKey="count" radius={[10, 10, 0, 0]} fill="#6366f1" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="note">Table view is available below.</div>
        </div>

        <div className="card">
          <div className="cardTitle">Category-wise business count (Top 10)</div>
          <div className="chartWrap">
            <ResponsiveContainer>
              <BarChart
                data={categoryWise}
                margin={{ top: 10, right: 14, left: 0, bottom: 26 }}
              >
                <CartesianGrid
                  stroke="rgba(255,255,255,.08)"
                  strokeDasharray="3 3"
                />
                <XAxis
  		dataKey="name"
  		interval={0}                 // force show all ticks
  		tickFormatter={(v) => (v.length > 10 ? v.slice(0, 10) + "…" : v)}
  		angle={-25}
  		textAnchor="end"
  		height={60}
  		tick={{ fill: "rgba(234,242,255,.8)", fontSize: 12 }}
/>
                <YAxis
                  tick={{ fill: "rgba(234,242,255,.75)", fontSize: 12 }}
                />
                <Tooltip
                  contentStyle={{
                    background: "#0b1628",
                    border: "1px solid rgba(255,255,255,.10)",
                    borderRadius: 12,
                  }}
                  labelStyle={{ color: "rgba(234,242,255,.85)" }}
                />
                <Bar dataKey="count" radius={[10, 10, 0, 0]} fill="#22c55e" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="note">Top 10 shown for readability.</div>
        </div>

        <div className="card">
          <div className="cardTitle">Source-wise business count</div>
          <div className="chartWrap">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={sourceWise}
                  dataKey="count"
                  nameKey="name"
                  innerRadius={70}
                  outerRadius={120}
                  paddingAngle={2}
                >
                  {sourceWise.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>

                <Tooltip
                  contentStyle={{
                    background: "#0b1628",
                    border: "1px solid rgba(255,255,255,.10)",
                    borderRadius: 12,
                  }}
                  labelStyle={{ color: "rgba(234,242,255,.85)" }}
                />

                {/* Legend improvement: spacing + font */}
                <Legend
                  verticalAlign="bottom"
                  height={58}
                  wrapperStyle={{
                    color: "rgba(234,242,255,.78)",
                    fontSize: 12,
                    lineHeight: "16px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="note">Donut chart improves label visibility.</div>
        </div>
      </div>

      {/* TABLES */}
      <div className="gridTables">
        <DataTable title="City-wise (Top 10)" rows={cityWise} />
        <DataTable title="Category-wise (Top 10)" rows={categoryWise} />
        <DataTable title="Source-wise" rows={sourceWise} />
      </div>
    </div>
  );
}