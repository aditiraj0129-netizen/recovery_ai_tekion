import { useMemo, useState } from 'react'
import { HERO_PART_ID } from '../constants/hero'
import type { InventoryRow } from '../types/api'
import { formatWhen, titleCase } from '../utils/format'
import { confidenceTone } from '../utils/tones'
import { Badge, DataTable, EmptyRow, StatusBadge, Td } from './ui'

const SHORT_LOCATION: Record<string, string> = {
  'LOC-A': 'Store A',
  'LOC-B': 'Store B',
  'LOC-C': 'Store C',
}

interface PartLine {
  part_id: string
  part_name: string
  part_type: string
  byLocation: Record<string, InventoryRow>
}

export function InventoryTable({
  inventory,
  scenarioDate,
}: {
  inventory: InventoryRow[]
  scenarioDate: string
}) {
  const [query, setQuery] = useState('')

  const { lines, locationIds } = useMemo(() => {
    const map = new Map<string, PartLine>()
    const locations = new Set<string>()
    for (const row of inventory) {
      locations.add(row.location_id)
      const line = map.get(row.part_id) ?? {
        part_id: row.part_id,
        part_name: row.part_name,
        part_type: row.part_type,
        byLocation: {},
      }
      line.byLocation[row.location_id] = row
      map.set(row.part_id, line)
    }
    return { lines: [...map.values()], locationIds: [...locations].sort() }
  }, [inventory])

  const needle = query.trim().toLowerCase()
  const visible = lines.filter(
    (line) => !needle || line.part_id.toLowerCase().includes(needle) || line.part_name.toLowerCase().includes(needle),
  )

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search parts…"
          aria-label="Search parts"
          className="w-60 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm shadow-sm focus:border-slate-500 focus:outline-none"
        />
        <span className="text-xs text-slate-500">
          {visible.length} parts · each cell shows available / on hand · stock source is the system count
        </span>
      </div>

      <DataTable
        columns={[
          { label: 'Part' },
          { label: 'Type' },
          ...locationIds.map((id) => ({ label: SHORT_LOCATION[id] ?? id })),
        ]}
      >
        {visible.length === 0 && <EmptyRow colSpan={2 + locationIds.length} text="No parts match your search." />}
        {visible.map((line) => (
          <tr key={line.part_id} className={line.part_id === HERO_PART_ID ? 'bg-amber-50/40' : ''}>
            <Td>
              <div className="font-semibold text-slate-900">{line.part_name}</div>
              <div className="font-mono text-xs text-slate-500">{line.part_id}</div>
              {line.part_id === HERO_PART_ID && <Badge tone="amber">Hero part</Badge>}
            </Td>
            <Td>{line.part_type}</Td>
            {locationIds.map((id) => {
              const row = line.byLocation[id]
              if (!row) return <Td key={id}>n/a</Td>
              return (
                <Td key={id}>
                  <div className="font-semibold tabular-nums text-slate-900">
                    {row.available_quantity} / {row.quantity_on_hand}
                    {row.reserved_quantity > 0 && (
                      <span className="ml-1 text-xs font-normal text-slate-500">({row.reserved_quantity} reserved)</span>
                    )}
                  </div>
                  {row.stock_confidence !== 'known' && (
                    <div className="mt-0.5">
                      <StatusBadge value={row.stock_confidence} tones={confidenceTone} />
                    </div>
                  )}
                  {row.expected_arrival && (
                    <div className="mt-0.5 text-xs text-slate-500">
                      {row.quantity_on_hand === 0 ? 'ETA' : 'Next'} {formatWhen(row.expected_arrival, scenarioDate)}
                    </div>
                  )}
                  {row.stock_confidence === 'unverified' && (
                    <div className="mt-0.5 text-xs text-red-600">{titleCase('count not verified')}</div>
                  )}
                </Td>
              )
            })}
          </tr>
        ))}
      </DataTable>
    </div>
  )
}
