import type { DepartmentNode, PersonnelItem } from '@/types'

export type DeptPathRecord = Pick<
  PersonnelItem,
  | 'dept_l1_name'
  | 'dept_l2_name'
  | 'dept_l3_name'
  | 'dept_l4_name'
  | 'dept_l5_name'
  | 'dept_l6_name'
  | 'dept_l7_name'
>

export interface PermissionSummary {
  total: number
  withPermission: number
  withoutPermission: number
  coverageRate: number
}

export interface ChildDeptStats {
  name: string
  withPermission: number
  withoutPermission: number
  total: number
}

export function findDeptPath(nodes: DepartmentNode[], targetId: number, acc: string[] = []): string[] | null {
  for (const node of nodes) {
    const path = [...acc, node.name]
    if (node.id === targetId) return path
    if (node.children?.length) {
      const found = findDeptPath(node.children, targetId, path)
      if (found) return found
    }
  }
  return null
}

export function findDeptNode(nodes: DepartmentNode[], targetId: number): DepartmentNode | null {
  for (const node of nodes) {
    if (node.id === targetId) return node
    if (node.children?.length) {
      const found = findDeptNode(node.children, targetId)
      if (found) return found
    }
  }
  return null
}

export function personMatchesDeptPath(person: DeptPathRecord, path: string[]): boolean {
  for (let i = 0; i < path.length; i++) {
    const name = person[`dept_l${i + 1}_name` as keyof DeptPathRecord] as string | null
    if (name !== path[i]) return false
  }
  return true
}

export function filterByDeptPath<T extends DeptPathRecord>(records: T[], path: string[]): T[] {
  if (path.length === 0) return records
  return records.filter((item) => personMatchesDeptPath(item, path))
}

export function filterPersonnelByDeptPath(personnel: PersonnelItem[], path: string[]): PersonnelItem[] {
  return filterByDeptPath(personnel, path)
}

export function computePermissionSummary(
  personnel: PersonnelItem[],
  permittedEmpNos: Set<string>
): PermissionSummary {
  const total = personnel.length
  const withPermission = personnel.filter((p) => permittedEmpNos.has(p.emp_no)).length
  const withoutPermission = total - withPermission
  const coverageRate = total > 0 ? Math.round((withPermission / total) * 1000) / 10 : 0
  return { total, withPermission, withoutPermission, coverageRate }
}

export function computeChildDeptStats(
  personnel: PersonnelItem[],
  parentPath: string[],
  children: DepartmentNode[],
  permittedEmpNos: Set<string>
): ChildDeptStats[] {
  return children.map((child) => {
    const childPath = [...parentPath, child.name]
    const scoped = filterPersonnelByDeptPath(personnel, childPath)
    const withPermission = scoped.filter((p) => permittedEmpNos.has(p.emp_no)).length
    const total = scoped.length
    return {
      name: child.name,
      withPermission,
      withoutPermission: total - withPermission,
      total
    }
  })
}
