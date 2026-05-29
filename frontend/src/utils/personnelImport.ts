import type { ImportFailureItem } from '@/types'

/** 与后端 parse_emp_nos 保持一致 */
export function parseEmpNos(text: string): string[] {
  const seen = new Set<string>()
  const result: string[] = []
  for (const part of text.split(/[,，\s]+/)) {
    const empNo = part.trim()
    if (empNo && !seen.has(empNo)) {
      seen.add(empNo)
      result.push(empNo)
    }
  }
  return result
}

/** 每批工号数：单批 HR 查询在可控时间内完成，避免前端超时 */
export const PERSONNEL_IMPORT_CHUNK_SIZE = 10

/** 单批请求超时（毫秒），需大于 HR 单条超时 × 批次大小 */
export const PERSONNEL_IMPORT_CHUNK_TIMEOUT_MS = 90_000

export function chunkEmpNos(empNos: string[], size = PERSONNEL_IMPORT_CHUNK_SIZE): string[][] {
  const chunks: string[][] = []
  for (let i = 0; i < empNos.length; i += size) {
    chunks.push(empNos.slice(i, i + size))
  }
  return chunks
}

export interface PersonnelImportProgress {
  processed: number
  total: number
  importedCount: number
  failureCount: number
  cancelled: boolean
}

export interface PersonnelImportResult {
  imported_count: number
  failures: ImportFailureItem[]
  cancelled: boolean
}
