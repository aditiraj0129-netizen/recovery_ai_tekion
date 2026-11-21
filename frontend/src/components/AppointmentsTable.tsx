import { useState } from 'react'
import type { Appointment, ConsentStatus } from '../types/api'
import { formatWhen } from '../utils/format'
import { consentTone } from '../utils/tones'
import { DataTable, EmptyRow, StatusBadge, Td } from './ui'

const CONSENT_FILTERS: { value: ConsentStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'declined', label: 'Declined' },
]

export function AppointmentsTable({
  appointments,
  scenarioDate,
}: {
  appointments: Appointment[]
  scenarioDate: string
}) {
  const [filter, setFilter] = useState<ConsentStatus | 'all'>('all')
  const rows = appointments.filter((a) => filter === 'all' || a.consent_status === filter)

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        {CONSENT_FILTERS.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => setFilter(option.value)}
            aria-pressed={filter === option.value}
            className={`rounded-full px-3 py-1 text-xs font-medium ring-1 ring-inset transition ${
              filter === option.value
                ? 'bg-slate-900 text-white ring-slate-900'
                : 'bg-white text-slate-600 ring-slate-300 hover:bg-slate-50'
            }`}
          >
            {option.label}
          </button>
        ))}
        <span className="ml-auto text-xs text-slate-500">
          Showing {rows.length} of {appointments.length} · consent status is shown only; no changes are proposed yet
        </span>
      </div>

      <DataTable
        columns={[
          { label: 'Appointment' },
          { label: 'RO' },
          { label: 'Scheduled' },
          { label: 'Promised' },
          { label: 'Customer preference' },
          { label: 'Consent' },
        ]}
      >
        {rows.length === 0 && <EmptyRow colSpan={6} text="No appointments match this filter." />}
        {rows.map((appointment) => (
          <tr key={appointment.appointment_id} className={appointment.ro_id === '48240' ? 'bg-amber-50/40' : ''}>
            <Td className="font-semibold text-slate-900">{appointment.appointment_id}</Td>
            <Td>{appointment.ro_id}</Td>
            <Td className="whitespace-nowrap">{formatWhen(appointment.scheduled_at, scenarioDate)}</Td>
            <Td className="whitespace-nowrap">{formatWhen(appointment.promised_at, scenarioDate)}</Td>
            <Td>{appointment.customer_preference ?? <span className="text-slate-400">None</span>}</Td>
            <Td>
              <StatusBadge value={appointment.consent_status} tones={consentTone} />
            </Td>
          </tr>
        ))}
      </DataTable>
    </div>
  )
}
