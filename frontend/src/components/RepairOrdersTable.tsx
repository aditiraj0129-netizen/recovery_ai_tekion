import { useMemo, useState } from 'react'
import { HERO_DIRECT_RO_IDS, HERO_INDIRECT_RO_IDS } from '../constants/hero'
import type { Appointment, RepairOrder, RepairOrderStatus } from '../types/api'
import { formatMinutes, formatTime, formatWhen } from '../utils/format'
import { repairOrderTone } from '../utils/tones'
import { Badge, Chips, DataTable, EmptyRow, StatusBadge, Td } from './ui'

const STATUS_FILTERS: { value: RepairOrderStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'waiting', label: 'Waiting' },
  { value: 'in_progress', label: 'In progress' },
  { value: 'completed', label: 'Completed' },
]

// Neutral marker only: whether a repair order is directly or indirectly affected is
// decided by the Phase 2 blast-radius engine, not by this list.
function HeroTag({ roId }: { roId: string }) {
  if (HERO_DIRECT_RO_IDS.includes(roId) || HERO_INDIRECT_RO_IDS.includes(roId)) {
    return <Badge tone="amber">Hero scenario</Badge>
  }
  return null
}

export function RepairOrdersTable({
  repairOrders,
  appointments,
  scenarioDate,
}: {
  repairOrders: RepairOrder[]
  appointments: Appointment[]
  scenarioDate: string
}) {
  const [filter, setFilter] = useState<RepairOrderStatus | 'all'>('all')
  const [heroOnly, setHeroOnly] = useState(false)
  const hasAppointment = useMemo(() => new Set(appointments.map((a) => a.ro_id)), [appointments])

  const rows = repairOrders.filter(
    (ro) =>
      (filter === 'all' || ro.status === filter) &&
      (!heroOnly || HERO_DIRECT_RO_IDS.includes(ro.ro_id) || HERO_INDIRECT_RO_IDS.includes(ro.ro_id)),
  )

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        {STATUS_FILTERS.map((option) => (
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
        <label className="ml-2 flex items-center gap-1.5 text-xs text-slate-600">
          <input
            type="checkbox"
            checked={heroOnly}
            onChange={(event) => setHeroOnly(event.target.checked)}
            className="h-3.5 w-3.5 rounded border-slate-300"
          />
          Hero scenario only
        </label>
        <span className="ml-auto text-xs text-slate-500">
          Showing {rows.length} of {repairOrders.length}
        </span>
      </div>

      <DataTable
        columns={[
          { label: 'RO' },
          { label: 'Status' },
          { label: 'Work' },
          { label: 'Parts' },
          { label: 'Technician / bay' },
          { label: 'Scheduled' },
          { label: 'Promised' },
          { label: 'Appt' },
        ]}
      >
        {rows.length === 0 && <EmptyRow colSpan={8} text="No repair orders match this filter." />}
        {rows.map((ro) => (
          <tr key={ro.ro_id} className={HERO_DIRECT_RO_IDS.includes(ro.ro_id) || HERO_INDIRECT_RO_IDS.includes(ro.ro_id) ? 'bg-amber-50/40' : ''}>
            <Td>
              <div className="font-semibold text-slate-900">{ro.ro_id}</div>
              <div className="mt-1 flex flex-wrap gap-1">
                <HeroTag roId={ro.ro_id} />
                {ro.is_waiting_customer && <Badge tone="blue">Waiting customer</Badge>}
              </div>
            </Td>
            <Td>
              <StatusBadge value={ro.status} tones={repairOrderTone} />
            </Td>
            <Td>
              <Chips items={ro.required_skills} />
              <div className="mt-1 text-xs text-slate-500">{formatMinutes(ro.estimated_duration_minutes)}</div>
            </Td>
            <Td>
              <div className="flex flex-wrap gap-1">
                {ro.required_parts.length === 0 && <span className="text-xs text-slate-400">None</span>}
                {ro.required_parts.map((part) => (
                  <span key={part.part_id} className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs text-slate-600">
                    {part.part_id}
                  </span>
                ))}
              </div>
            </Td>
            <Td>
              <div>{ro.assigned_technician_id ?? 'Unassigned'}</div>
              <div className="text-xs text-slate-500">{ro.assigned_bay_id ?? 'No bay'}</div>
            </Td>
            <Td className="whitespace-nowrap">
              {ro.scheduled_start && ro.scheduled_end
                ? `${formatTime(ro.scheduled_start)}–${formatTime(ro.scheduled_end)}`
                : 'n/a'}
              {ro.scheduled_start && (
                <div className="text-xs text-slate-500">{formatWhen(ro.scheduled_start, scenarioDate).split(' ')[0]}</div>
              )}
            </Td>
            <Td className="whitespace-nowrap">{formatWhen(ro.promised_at, scenarioDate)}</Td>
            <Td>{hasAppointment.has(ro.ro_id) ? <Badge tone="slate">Booked</Badge> : <span className="text-xs text-slate-400">Walk-in</span>}</Td>
          </tr>
        ))}
      </DataTable>
    </div>
  )
}
