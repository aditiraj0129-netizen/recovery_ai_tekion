// These types mirror the Pydantic response models in backend/app/schemas/dealership.py.
// If the backend response shape changes, update this file.

export type RepairOrderStatus = 'waiting' | 'in_progress' | 'blocked' | 'completed'
export type TechnicianAvailability = 'available' | 'busy' | 'absent'
export type BayStatus = 'available' | 'occupied'
export type ConsentStatus = 'pending' | 'approved' | 'declined'
export type DisruptionStatus = 'active' | 'scheduled' | 'resolved'
export type Severity = 'low' | 'medium' | 'high' | 'critical'
export type StockConfidence = 'known' | 'estimated' | 'unverified'

export interface RepairOrderPart {
  part_id: string
  quantity: number
}

export interface RepairOrder {
  ro_id: string
  vehicle_id: string
  customer_id: string
  required_parts: RepairOrderPart[]
  required_skills: string[]
  estimated_duration_minutes: number
  status: RepairOrderStatus
  promised_at: string
  priority: number
  assigned_technician_id: string | null
  assigned_bay_id: string | null
  scheduled_start: string | null
  scheduled_end: string | null
  created_at: string
  is_waiting_customer: boolean
  is_synthetic: boolean
}

export interface Technician {
  technician_id: string
  name: string
  skills: string[]
  shift_start: string
  shift_end: string
  availability: TechnicianAvailability
  efficiency_factor: number
  is_synthetic: boolean
}

export interface Bay {
  bay_id: string
  supported_work: string[]
  available_from: string
  available_until: string
  status: BayStatus
  is_synthetic: boolean
}

export interface InventoryRow {
  part_id: string
  part_name: string
  part_type: string
  location_id: string
  location_name: string
  supplier_id: string | null
  quantity_on_hand: number
  reserved_quantity: number
  available_quantity: number
  expected_arrival: string | null
  stock_confidence: StockConfidence
  unit_cost: number
  is_synthetic: boolean
}

export interface Appointment {
  appointment_id: string
  ro_id: string
  scheduled_at: string
  promised_at: string
  customer_preference: string | null
  consent_status: ConsentStatus
  is_synthetic: boolean
}

export interface Disruption {
  disruption_id: string
  disruption_type: string
  affected_resource_type: string
  affected_resource_id: string
  start_time: string
  severity: Severity
  expected_duration_minutes: number | null
  status: DisruptionStatus
  related_part_id: string | null
  related_technician_id: string | null
  related_bay_id: string | null
  related_location_id: string | null
  description: string
  details: Record<string, unknown>
  is_synthetic: boolean
}

export interface Dashboard {
  scenario_date: string
  scenario_clock: string
  is_synthetic: boolean
  repair_orders_total: number
  repair_orders_by_status: Record<string, number>
  waiting_customers: number
  technicians_total: number
  technicians_by_availability: Record<string, number>
  bays_total: number
  bays_by_status: Record<string, number>
  appointments_total: number
  appointments_by_consent: Record<string, number>
  disruptions_total: number
  disruptions_by_status: Record<string, number>
  parts_total: number
}

export interface DealershipData {
  dashboard: Dashboard
  repairOrders: RepairOrder[]
  technicians: Technician[]
  bays: Bay[]
  inventory: InventoryRow[]
  appointments: Appointment[]
  disruptions: Disruption[]
}
