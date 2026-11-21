import type { Bay, Technician } from '../types/api'
import { formatTime } from '../utils/format'
import { availabilityTone, bayTone } from '../utils/tones'
import { Card, Chips, DataTable, StatusBadge, Td } from './ui'

export function ResourcesPanel({ technicians, bays }: { technicians: Technician[]; bays: Bay[] }) {
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      <Card title={`Technicians (${technicians.length})`} subtitle="Skills, shifts and availability at 09:40">
        <DataTable columns={[{ label: 'ID' }, { label: 'Name' }, { label: 'Skills' }, { label: 'Shift' }, { label: 'Status' }]}>
          {technicians.map((tech) => (
            <tr key={tech.technician_id} className={tech.technician_id === 'T03' ? 'bg-amber-50/40' : ''}>
              <Td className="font-semibold text-slate-900">{tech.technician_id}</Td>
              <Td>{tech.name}</Td>
              <Td>
                <Chips items={tech.skills} />
              </Td>
              <Td className="whitespace-nowrap">
                {formatTime(tech.shift_start)}–{formatTime(tech.shift_end)}
              </Td>
              <Td>
                <StatusBadge value={tech.availability} tones={availabilityTone} />
              </Td>
            </tr>
          ))}
        </DataTable>
        <p className="mt-2 text-xs text-slate-500">
          Highlighted: T03 is the only technician with the cooling system skill.
        </p>
      </Card>

      <Card title={`Service bays (${bays.length})`} subtitle="Supported work and operating hours">
        <DataTable columns={[{ label: 'Bay' }, { label: 'Supported work' }, { label: 'Hours' }, { label: 'Status' }]}>
          {bays.map((bay) => (
            <tr key={bay.bay_id}>
              <Td className="font-semibold text-slate-900">{bay.bay_id}</Td>
              <Td>
                <Chips items={bay.supported_work} />
              </Td>
              <Td className="whitespace-nowrap">
                {formatTime(bay.available_from)}–{formatTime(bay.available_until)}
              </Td>
              <Td>
                <StatusBadge value={bay.status} tones={bayTone} />
              </Td>
            </tr>
          ))}
        </DataTable>
      </Card>
    </div>
  )
}
