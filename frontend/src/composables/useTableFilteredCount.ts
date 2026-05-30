import { computed, ref, type Ref } from 'vue'
import type { TableInstance } from 'element-plus'

function cellText(row: Record<string, unknown>, columnKey: string): string {
  const raw = row[columnKey]
  if (raw == null) return ''
  return typeof raw === 'string' ? raw : String(raw)
}

/** 与 el-table column filters 一致：列间 AND，列内多选 OR */
export function useTableFilteredCount<T extends Record<string, unknown>>(data: Ref<T[]>) {
  const activeFilters = ref<Record<string, string[]>>({})

  const onFilterChange = (filters: Record<string, string[]>) => {
    activeFilters.value = { ...filters }
  }

  const resetFilters = () => {
    activeFilters.value = {}
  }

  const filteredRows = computed(() => {
    let rows = data.value
    for (const [columnKey, values] of Object.entries(activeFilters.value)) {
      if (!values?.length) continue
      const allowed = new Set(values)
      rows = rows.filter((row) => allowed.has(cellText(row, columnKey)))
    }
    return rows
  })

  const totalCount = computed(() => data.value.length)
  const displayCount = computed(() => filteredRows.value.length)
  const isFiltered = computed(() => displayCount.value !== totalCount.value)

  const clearTableFilters = (tableRef: TableInstance | undefined) => {
    // 服务端筛选由 filtered-value 控制，勿调用 clearFilter()，否则易触发 parentNode 空引用
    void tableRef
    resetFilters()
  }

  return {
    totalCount,
    displayCount,
    isFiltered,
    onFilterChange,
    resetFilters,
    clearTableFilters
  }
}
