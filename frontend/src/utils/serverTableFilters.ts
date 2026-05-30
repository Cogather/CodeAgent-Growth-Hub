import { DEPT_DISPLAY_LEVELS } from '@/types'

/** 从 el-table filter-change 解析部门筛选，仅在有变化时返回 true */
export function mergeDeptFiltersFromTable<T extends Record<string, string | undefined>>(
  tableFilters: Record<string, string[]>,
  current: T
): { next: T; changed: boolean } {
  const next = { ...current }
  let changed = false

  for (const level of DEPT_DISPLAY_LEVELS) {
    const key = `dept_l${level}_name` as keyof T & string
    const values = tableFilters[key]
    const newVal = !values?.length ? undefined : values[0]
    if (next[key] !== newVal) {
      changed = true
      if (newVal === undefined) {
        delete (next as Record<string, string | undefined>)[key]
      } else {
        ;(next as Record<string, string | undefined>)[key] = newVal
      }
    }
  }

  return { next, changed }
}
