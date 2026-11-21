import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import type { Dashboard } from '../types/api'
import { titleCase } from '../utils/format'
import { Card, StatCard } from './ui'

const STATUS_COLORS: Record<string, string> = {
  waiting: '#64748b',
  in_progress: '#2563eb',
  blocked: '#dc2626',
  completed: '#059669',
}

function breakdown(counts: Record<string, number>): string {
  return Object.entries(counts)
    .map(([key, count]) => `${count} ${titleCase(key).toLowerCase()}`)
    .join(' · ')
}

export function Overview({ dashboard }: { dashboard: Dashboard }) {
  const chartData = Object.entries(dashboard.repair_orders_by_status).map(([status, count]) => ({
    status,
    label: titleCase(status),
    count,
  }))

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        <StatCard
          label="Repair orders"
          value={dashboard.repair_orders_total}
          detail={`${dashboard.waiting_customers} with a waiting customer`}
        />
        <StatCard
          label="Technicians"
          value={dashboard.technicians_total}
          detail={breakdown(dashboard.technicians_by_availability)}
        />
        <StatCard
          label="Service bays"
          value={dashboard.bays_total}
          detail={breakdown(dashboard.bays_by_status)}
        />
        <StatCard
          label="Appointments"
          value={dashboard.appointments_total}
          detail={breakdown(dashboard.appointments_by_consent)}
        />
        <StatCard
          label="Disruptions"
          value={dashboard.disruptions_total}
          detail={breakdown(dashboard.disruptions_by_status)}
        />
      </div>

      <Card title="Repair orders by status" subtitle={`${dashboard.parts_total} unique parts in the catalog`}>
        <div className="flex flex-col items-center gap-4 sm:flex-row">
          <div className="h-44 w-44 shrink-0" role="img" aria-label="Repair orders by status">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  dataKey="count"
                  nameKey="label"
                  innerRadius={42}
                  outerRadius={70}
                  paddingAngle={2}
                  isAnimationActive={false}
                >
                  {chartData.map((entry) => (
                    <Cell key={entry.status} fill={STATUS_COLORS[entry.status] ?? '#94a3b8'} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <ul className="space-y-2 text-sm">
            {chartData.map((entry) => (
              <li key={entry.status} className="flex items-center gap-2">
                <span
                  className="h-3 w-3 rounded-sm"
                  style={{ backgroundColor: STATUS_COLORS[entry.status] ?? '#94a3b8' }}
                />
                <span className="w-24 text-slate-600">{entry.label}</span>
                <span className="font-semibold tabular-nums text-slate-900">{entry.count}</span>
              </li>
            ))}
          </ul>
        </div>
      </Card>
    </div>
  )
}
