import { useCallback, useEffect, useState } from 'react'
import { fetchDealershipData } from '../api/client'
import type { DealershipData } from '../types/api'

export type DataState =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; data: DealershipData }

/** Fetches all dashboard data once on mount; `reload` fetches it again. */
export function useDealershipData() {
  const [state, setState] = useState<DataState>({ status: 'loading' })

  const load = useCallback(async () => {
    try {
      const data = await fetchDealershipData()
      setState({ status: 'ready', data })
    } catch {
      setState({
        status: 'error',
        message:
          'Cannot load data from the Recovery AI API. Check that the backend is running (port 8001) and try again.',
      })
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const reload = useCallback(() => {
    setState({ status: 'loading' })
    void load()
  }, [load])

  return { state, reload }
}
