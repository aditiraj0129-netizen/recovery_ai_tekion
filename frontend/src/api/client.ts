import type {
  Appointment,
  Bay,
  Dashboard,
  DealershipData,
  Disruption,
  InventoryRow,
  RepairOrder,
  Technician,
} from '../types/api'

// Empty by default: requests go to the same origin and Vite's dev proxy forwards /api/*
// to the backend. Set VITE_API_BASE_URL (e.g. http://127.0.0.1:8001) to call it directly.
const BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? ''

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`)
  if (!response.ok) {
    throw new ApiError(response.status, `GET ${path} failed with status ${response.status}`)
  }
  return (await response.json()) as T
}

/** Loads everything the dashboard shows, in parallel. */
export async function fetchDealershipData(): Promise<DealershipData> {
  const [dashboard, repairOrders, technicians, bays, inventory, appointments, disruptions] =
    await Promise.all([
      get<Dashboard>('/api/dashboard'),
      get<RepairOrder[]>('/api/repair-orders'),
      get<Technician[]>('/api/technicians'),
      get<Bay[]>('/api/bays'),
      get<InventoryRow[]>('/api/inventory'),
      get<Appointment[]>('/api/appointments'),
      get<Disruption[]>('/api/disruptions'),
    ])
  return { dashboard, repairOrders, technicians, bays, inventory, appointments, disruptions }
}
