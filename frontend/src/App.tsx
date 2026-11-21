import { useState } from 'react'
import { AppointmentsTable } from './components/AppointmentsTable'
import { DisruptionsTable } from './components/DisruptionsTable'
import { InventoryTable } from './components/InventoryTable'
import { Overview } from './components/Overview'
import { RepairOrdersTable } from './components/RepairOrdersTable'
import { ResourcesPanel } from './components/ResourcesPanel'
import { useDealershipData } from './hooks/useDealershipData'
import type { DealershipData } from './types/api'

type TabId = 'overview' | 'repair-orders' | 'resources' | 'inventory' | 'appointments' | 'disruptions'

const TABS: { id: TabId; label: string; count: (data: DealershipData) => number | null }[] = [
  { id: 'overview', label: 'Overview', count: () => null },
  { id: 'repair-orders', label: 'Repair orders', count: (d) => d.repairOrders.length },
  { id: 'resources', label: 'Technicians & bays', count: (d) => d.technicians.length + d.bays.length },
  { id: 'inventory', label: 'Parts inventory', count: (d) => new Set(d.inventory.map((r) => r.part_id)).size },
  { id: 'appointments', label: 'Appointments', count: (d) => d.appointments.length },
  { id: 'disruptions', label: 'Disruptions', count: (d) => d.disruptions.length },
]

function App() {
  const { state, reload } = useDealershipData()
  const [tab, setTab] = useState<TabId>('overview')

  return (
    <div className="min-h-screen">
      <div className="bg-amber-100 px-4 py-1.5 text-center text-xs font-medium text-amber-900">
        Synthetic, illustrative data. Recovery AI is a prototype and is not connected to Tekion ARC or any real dealership.
      </div>

      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-4">
          <div>
            <h1 className="text-xl font-semibold tracking-tight text-slate-900">Recovery AI</h1>
            <p className="text-sm text-slate-500">Service operations · Milestone 1 data foundation</p>
          </div>
          <div className="flex items-center gap-3">
            {state.status === 'ready' && (
              <div className="rounded-lg bg-slate-100 px-3 py-1.5 text-sm text-slate-700">
                Scenario clock <span className="font-semibold tabular-nums">{state.data.dashboard.scenario_clock}</span>
                <span className="text-slate-500"> · {state.data.dashboard.scenario_date}</span>
              </div>
            )}
            <button
              type="button"
              onClick={reload}
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
            >
              Refresh
            </button>
          </div>
        </div>

        {state.status === 'ready' && (
          <nav className="mx-auto max-w-7xl overflow-x-auto px-4" aria-label="Dashboard sections">
            <div className="flex gap-1">
              {TABS.map((item) => {
                const count = item.count(state.data)
                const active = tab === item.id
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setTab(item.id)}
                    aria-current={active ? 'page' : undefined}
                    className={`whitespace-nowrap border-b-2 px-3 py-2 text-sm font-medium transition ${
                      active
                        ? 'border-slate-900 text-slate-900'
                        : 'border-transparent text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    {item.label}
                    {count !== null && <span className="ml-1.5 text-xs text-slate-400">{count}</span>}
                  </button>
                )
              })}
            </div>
          </nav>
        )}
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6">
        {state.status === 'loading' && <p className="text-sm text-slate-500">Loading dealership data…</p>}

        {state.status === 'error' && (
          <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
            <p className="font-semibold">Could not load data</p>
            <p className="mt-1">{state.message}</p>
            <button
              type="button"
              onClick={reload}
              className="mt-3 rounded-lg bg-red-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-800"
            >
              Try again
            </button>
          </div>
        )}

        {state.status === 'ready' && (
          <>
            {tab === 'overview' && <Overview dashboard={state.data.dashboard} />}
            {tab === 'repair-orders' && (
              <RepairOrdersTable
                repairOrders={state.data.repairOrders}
                appointments={state.data.appointments}
                scenarioDate={state.data.dashboard.scenario_date}
              />
            )}
            {tab === 'resources' && <ResourcesPanel technicians={state.data.technicians} bays={state.data.bays} />}
            {tab === 'inventory' && (
              <InventoryTable inventory={state.data.inventory} scenarioDate={state.data.dashboard.scenario_date} />
            )}
            {tab === 'appointments' && (
              <AppointmentsTable
                appointments={state.data.appointments}
                scenarioDate={state.data.dashboard.scenario_date}
              />
            )}
            {tab === 'disruptions' && (
              <DisruptionsTable
                disruptions={state.data.disruptions}
                scenarioDate={state.data.dashboard.scenario_date}
              />
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default App
