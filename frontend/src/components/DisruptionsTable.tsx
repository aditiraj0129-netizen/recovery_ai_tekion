import { useState } from 'react'
import type { Disruption, DisruptionStatus } from '../types/api'
import { formatMinutes, formatWhen, titleCase } from '../utils/format'
import { disruptionStatusTone, severityTone } from '../utils/tones'
import { DataTable, EmptyRow, StatusBadge, Td } from './ui'

const STATUS_FILTERS: { value: DisruptionStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'scheduled', label: 'Scheduled' },
  { value: 'resolved', label: 'Resolved' },
]

export function DisruptionsTable({
  disruptions,
  scenarioDate,
}: {
  disruptions: Disruption[]
  scenarioDate: string
}) {
  const [filter, setFilter] = useState<DisruptionStatus | 'all'>('all')
  const rows = disruptions.filter((d) => filter === 'all' || d.status === filter)

  return (
    <div className="space-y-3">
      <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
        <strong>Seeded data only.</strong> Disruptions here are pre-loaded records. Nothing detects, analyses or recovers from
        them yet. D-001 (09:40 pump backorder) and D-002 (10:38 Store B count failure) are dormant hero records.
      </div>

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
        <span className="ml-auto text-xs text-slate-500">
          Showing {rows.length} of {disruptions.length}
        </span>
      </div>

      <DataTable
        columns={[
          { label: 'ID' },
          { label: 'Type' },
          { label: 'Affects' },
          { label: 'Starts' },
          { label: 'Severity' },
          { label: 'Duration' },
          { label: 'Status' },
          { label: 'Description' },
        ]}
      >
        {rows.length === 0 && <EmptyRow colSpan={8} text="No disruptions match this filter." />}
        {rows.map((d) => (
          <tr key={d.disruption_id} className={d.disruption_id === 'D-001' || d.disruption_id === 'D-002' ? 'bg-amber-50/40' : ''}>
            <Td className="whitespace-nowrap font-semibold text-slate-900">{d.disruption_id}</Td>
            <Td>{titleCase(d.disruption_type)}</Td>
            <Td className="whitespace-nowrap">
              <div className="text-xs text-slate-500">{titleCase(d.affected_resource_type)}</div>
              <div className="font-mono text-xs">{d.affected_resource_id}</div>
            </Td>
            <Td className="whitespace-nowrap">{formatWhen(d.start_time, scenarioDate)}</Td>
            <Td>
              <StatusBadge value={d.severity} tones={severityTone} />
            </Td>
            <Td className="whitespace-nowrap">{formatMinutes(d.expected_duration_minutes)}</Td>
            <Td>
              <StatusBadge value={d.status} tones={disruptionStatusTone} />
            </Td>
            <Td className="min-w-64">{d.description}</Td>
          </tr>
        ))}
      </DataTable>
    </div>
  )
}
