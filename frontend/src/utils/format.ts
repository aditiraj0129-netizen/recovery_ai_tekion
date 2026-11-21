/** Time and text helpers. Timestamps from the API are naive ISO strings (scenario local time). */

const MS_PER_DAY = 24 * 60 * 60 * 1000

function dayNumber(isoDate: string): number {
  return Date.parse(`${isoDate}T00:00:00Z`) / MS_PER_DAY
}

export function formatTime(iso: string): string {
  return iso.slice(11, 16)
}

/** "Today 17:00", "Tomorrow 12:00", "Yesterday 16:30", or "2026-03-08 09:00". */
export function formatWhen(iso: string, scenarioDate: string): string {
  const date = iso.slice(0, 10)
  const diff = dayNumber(date) - dayNumber(scenarioDate)
  const label = diff === 0 ? 'Today' : diff === 1 ? 'Tomorrow' : diff === -1 ? 'Yesterday' : date
  return `${label} ${formatTime(iso)}`
}

export function titleCase(value: string): string {
  const text = value.replaceAll('_', ' ')
  return text.charAt(0).toUpperCase() + text.slice(1)
}

const SKILL_LABELS: Record<string, string> = {
  ac_hvac: 'A/C & HVAC',
  tires_alignment: 'Tires & alignment',
  cooling_system: 'Cooling system',
  general_service: 'General service',
}

/** Readable label for a skill / work type such as `ac_hvac`. */
export function skillLabel(skill: string): string {
  return SKILL_LABELS[skill] ?? titleCase(skill)
}

export function formatMinutes(minutes: number | null): string {
  if (minutes === null) return 'n/a'
  if (minutes < 60) return `${minutes} min`
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  return rest === 0 ? `${hours} h` : `${hours} h ${rest} min`
}
