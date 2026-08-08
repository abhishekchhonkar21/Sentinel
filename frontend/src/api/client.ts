import type {
  ClearFaultResponse,
  FaultCatalogueEntry,
  InjectFaultResponse,
  SystemStatusResponse,
} from "../types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed (${response.status})`);
  }

  return response.json() as Promise<T>;
}

export async function fetchHealth(): Promise<{ status: string }> {
  return request("/api/v1/health");
}

export async function fetchFaults(): Promise<FaultCatalogueEntry[]> {
  return request("/api/v1/faults");
}

export async function fetchSystemStatus(): Promise<SystemStatusResponse> {
  return request("/api/v1/system-status");
}

export async function injectFault(faultId: string): Promise<InjectFaultResponse> {
  return request("/api/v1/inject-fault", {
    method: "POST",
    body: JSON.stringify({ fault_id: faultId }),
  });
}

export async function clearFault(service: string): Promise<ClearFaultResponse> {
  return request("/api/v1/clear-fault", {
    method: "POST",
    body: JSON.stringify({ service }),
  });
}
