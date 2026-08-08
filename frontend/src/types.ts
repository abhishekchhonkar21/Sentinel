export interface FaultCatalogueEntry {
  fault_id: string;
  description: string;
  injected_service: string;
  true_root_cause: string;
  expected_signal_type: string;
}

export interface InjectFaultResponse {
  fault_id: string;
  injected_at: string;
  status: string;
  injected_service: string;
  catalogue_entry: FaultCatalogueEntry | null;
}

export interface ClearFaultResponse {
  service: string;
  cleared_at: string;
  status: string;
}

export interface ServiceFaultStatus {
  service: string;
  state: Record<string, unknown>;
  active: boolean;
}

export interface LastFaultAction {
  action: string;
  fault_id: string | null;
  service: string;
  at: string;
}

export interface SystemStatusResponse {
  services: ServiceFaultStatus[];
  catalogue_count: number;
  last_action: LastFaultAction | null;
}
