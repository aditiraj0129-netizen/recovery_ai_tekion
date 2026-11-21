import type {
  BayStatus,
  ConsentStatus,
  DisruptionStatus,
  RepairOrderStatus,
  Severity,
  StockConfidence,
  TechnicianAvailability,
} from '../types/api'

export type Tone = 'slate' | 'blue' | 'green' | 'amber' | 'red'

export const repairOrderTone: Record<RepairOrderStatus, Tone> = {
  waiting: 'slate',
  in_progress: 'blue',
  blocked: 'red',
  completed: 'green',
}

export const availabilityTone: Record<TechnicianAvailability, Tone> = {
  available: 'green',
  busy: 'blue',
  absent: 'red',
}

export const bayTone: Record<BayStatus, Tone> = { available: 'green', occupied: 'blue' }

export const consentTone: Record<ConsentStatus, Tone> = {
  pending: 'amber',
  approved: 'green',
  declined: 'red',
}

export const disruptionStatusTone: Record<DisruptionStatus, Tone> = {
  active: 'red',
  scheduled: 'amber',
  resolved: 'green',
}

export const severityTone: Record<Severity, Tone> = {
  low: 'slate',
  medium: 'amber',
  high: 'red',
  critical: 'red',
}

export const confidenceTone: Record<StockConfidence, Tone> = {
  known: 'green',
  estimated: 'amber',
  unverified: 'red',
}
