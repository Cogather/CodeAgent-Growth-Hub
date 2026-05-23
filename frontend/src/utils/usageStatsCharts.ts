import type { DepartmentNode } from '@/types'
import type { UsageStatItem } from '@/types'
import {
  filterByDeptPath,
  findDeptNode,
  findDeptPath,
  type ChildDeptStats
} from '@/utils/zonePermissionStats'

export interface UsageSummary {
  total: number
  used: number
  unused: number
  usageRate: number
}

export function computeUsageSummary(items: UsageStatItem[]): UsageSummary {
  const total = items.length
  const used = items.filter((item) => item.usage_count > 0).length
  const unused = total - used
  const usageRate = total > 0 ? Math.round((used / total) * 1000) / 10 : 0
  return { total, used, unused, usageRate }
}

export function computeChildUsageStats(
  items: UsageStatItem[],
  parentPath: string[],
  children: DepartmentNode[]
): ChildDeptStats[] {
  return children.map((child) => {
    const childPath = [...parentPath, child.name]
    const scoped = filterByDeptPath(items, childPath)
    const used = scoped.filter((item) => item.usage_count > 0).length
    const total = scoped.length
    return {
      name: child.name,
      withPermission: used,
      withoutPermission: total - used,
      total
    }
  })
}

export { findDeptNode, findDeptPath, filterByDeptPath }
