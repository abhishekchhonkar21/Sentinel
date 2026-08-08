import { useCallback, useEffect, useMemo, useState } from "react";
import {
  clearFault,
  fetchFaults,
  fetchHealth,
  fetchSystemStatus,
  injectFault,
} from "./api/client";
import type {
  FaultCatalogueEntry,
  LastFaultAction,
  ServiceFaultStatus,
  SystemStatusResponse,
} from "./types";

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function activeKnobs(state: Record<string, unknown>): string[] {
  const labels: Record<string, string> = {
    null_deref: "null deref",
    latency_delay_ms: "latency",
    reject_charges: "reject charges",
    rate_limit_enabled: "rate limit",
    db_latency_delay_ms: "db latency",
    pool_stress_connections: "pool stress",
    processing_delay_ms: "processing delay",
  };

  return Object.entries(state)
    .filter(([key, value]) => {
      if (key === "error") return true;
      if (typeof value === "boolean") return value;
      if (typeof value === "number") return value > 0;
      return false;
    })
    .map(([key]) => labels[key] ?? key);
}

export default function App() {
  const [apiOk, setApiOk] = useState(false);
  const [faults, setFaults] = useState<FaultCatalogueEntry[]>([]);
  const [status, setStatus] = useState<SystemStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [serviceFilter, setServiceFilter] = useState("all");

  const refresh = useCallback(async () => {
    try {
      const [health, catalogue, systemStatus] = await Promise.all([
        fetchHealth(),
        fetchFaults(),
        fetchSystemStatus(),
      ]);
      setApiOk(health.status === "ok");
      setFaults(catalogue);
      setStatus(systemStatus);
      setError(null);
    } catch (err) {
      setApiOk(false);
      setError(err instanceof Error ? err.message : "Failed to reach fault-injection API");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval);
  }, [refresh]);

  const services = useMemo(() => {
    const names = new Set(faults.map((f) => f.injected_service));
    return Array.from(names).sort();
  }, [faults]);

  const filteredFaults = useMemo(() => {
    const q = search.trim().toLowerCase();
    return faults.filter((fault) => {
      if (serviceFilter !== "all" && fault.injected_service !== serviceFilter) {
        return false;
      }
      if (!q) return true;
      return (
        fault.fault_id.toLowerCase().includes(q) ||
        fault.description.toLowerCase().includes(q) ||
        fault.true_root_cause.toLowerCase().includes(q)
      );
    });
  }, [faults, search, serviceFilter]);

  const activeCount = status?.services.filter((s) => s.active).length ?? 0;
  const lastAction: LastFaultAction | null = status?.last_action ?? null;

  async function handleInject(faultId: string) {
    setBusyId(faultId);
    setError(null);
    try {
      await injectFault(faultId);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Injection failed");
    } finally {
      setBusyId(null);
    }
  }

  async function handleClear(service: string) {
    setBusyId(`clear-${service}`);
    setError(null);
    try {
      await clearFault(service);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Clear failed");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Sentinel Fault Control</h1>
          <p>Inject and clear faults in the toy system from the catalogue</p>
        </div>
        <span className={`status-pill ${apiOk ? "ok" : "error"}`}>
          <span className="status-dot" />
          {apiOk ? "API connected" : "API unreachable"}
        </span>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="summary-grid">
        <div className="summary-card">
          <div className="label">Catalogue</div>
          <div className="value">{status?.catalogue_count ?? faults.length}</div>
          <div className="sub">fault scenarios</div>
        </div>
        <div className="summary-card">
          <div className="label">Active faults</div>
          <div className="value" style={{ color: activeCount ? "var(--danger)" : "var(--success)" }}>
            {activeCount}
          </div>
          <div className="sub">services with injected state</div>
        </div>
        <div className="summary-card">
          <div className="label">Last action</div>
          <div className="value" style={{ fontSize: "1rem" }}>
            {lastAction ? lastAction.action : "—"}
          </div>
          <div className="sub">
            {lastAction
              ? `${lastAction.fault_id ?? lastAction.service} · ${formatTime(lastAction.at)}`
              : "no injections yet"}
          </div>
        </div>
      </div>

      <div className="layout">
        <section className="panel">
          <div className="panel-header">
            <h2>Fault catalogue</h2>
            <button className="btn-ghost" onClick={refresh} disabled={loading}>
              Refresh
            </button>
          </div>
          <div className="filter-row">
            <input
              type="search"
              placeholder="Search faults…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <select
              value={serviceFilter}
              onChange={(e) => setServiceFilter(e.target.value)}
            >
              <option value="all">All services</option>
              {services.map((svc) => (
                <option key={svc} value={svc}>{svc}</option>
              ))}
            </select>
          </div>
          <div className="panel-body">
            {loading ? (
              <div className="loading">Loading catalogue…</div>
            ) : filteredFaults.length === 0 ? (
              <div className="empty">No faults match your filters</div>
            ) : (
              <ul className="fault-list">
                {filteredFaults.map((fault) => (
                  <li key={fault.fault_id} className="fault-item">
                    <div className="fault-item-header">
                      <span className="fault-id">{fault.fault_id}</span>
                      <span className="fault-service">{fault.injected_service}</span>
                    </div>
                    <p className="fault-desc">{fault.description}</p>
                    <p className="fault-meta">
                      Root cause: {fault.true_root_cause} · Signal: {fault.expected_signal_type}
                    </p>
                    <div className="fault-actions">
                      <button
                        className="btn-primary"
                        disabled={busyId !== null}
                        onClick={() => handleInject(fault.fault_id)}
                      >
                        {busyId === fault.fault_id ? "Injecting…" : "Inject fault"}
                      </button>
                      <button
                        className="btn-danger"
                        disabled={busyId !== null}
                        onClick={() => handleClear(fault.injected_service)}
                      >
                        Clear service
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        <aside className="panel">
          <div className="panel-header">
            <h2>Live service state</h2>
            <span className="mono" style={{ fontSize: "0.75rem", color: "var(--muted)" }}>
              polls every 5s
            </span>
          </div>
          <ul className="service-list">
            {loading && !status ? (
              <li className="loading">Loading…</li>
            ) : (
              status?.services.map((svc: ServiceFaultStatus) => (
                <li key={svc.service} className="service-item">
                  <div className="service-row">
                    <span className="service-name">{svc.service}</span>
                    <span className={`badge ${svc.active ? "active" : "clean"}`}>
                      {svc.active ? "fault active" : "clean"}
                    </span>
                  </div>
                  {svc.active && (
                    <p className="fault-meta" style={{ margin: "0.25rem 0 0.4rem" }}>
                      Active: {activeKnobs(svc.state).join(", ")}
                    </p>
                  )}
                  <pre className="state-json">
                    {JSON.stringify(svc.state, null, 2)}
                  </pre>
                  {svc.active && (
                    <button
                      className="btn-danger"
                      style={{ marginTop: "0.5rem" }}
                      disabled={busyId !== null}
                      onClick={() => handleClear(svc.service)}
                    >
                      {busyId === `clear-${svc.service}` ? "Clearing…" : "Clear faults"}
                    </button>
                  )}
                </li>
              ))
            )}
          </ul>
        </aside>
      </div>
    </div>
  );
}
