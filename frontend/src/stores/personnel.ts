import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { OrganizationUnit, FSE, Personnel, PersonnelZone, DailyUsage, UsageSummary, AuditLog, ZoneType } from '@/types'

export const usePersonnelStore = defineStore('personnel', () => {
  const pdus = ref<OrganizationUnit[]>([])
  const devDepts = ref<OrganizationUnit[]>([])
  const fses = ref<FSE[]>([])
  const testFields = ref<OrganizationUnit[]>([])
  const personnelList = ref<Personnel[]>([])
  const dailyUsage = ref<DailyUsage[]>([])
  const auditLogs = ref<AuditLog[]>([])

  function initMockData() {
    const pdu1: OrganizationUnit = { id: 1, name: 'PDU-研发一部', type: 'pdu', parentId: null, pduContact: '张三', createdAt: '', updatedAt: '' }
    const pdu2: OrganizationUnit = { id: 2, name: 'PDU-研发二部', type: 'pdu', parentId: null, pduContact: '李四', createdAt: '', updatedAt: '' }
    pdus.value = [pdu1, pdu2]

    const dept1: OrganizationUnit = { id: 1, name: '前端开发组', type: 'devDept', parentId: 1, devContact: '王五', createdAt: '', updatedAt: '' }
    const dept2: OrganizationUnit = { id: 2, name: '后端开发组', type: 'devDept', parentId: 1, devContact: '赵六', createdAt: '', updatedAt: '' }
    const dept3: OrganizationUnit = { id: 3, name: '移动开发组', type: 'devDept', parentId: 2, devContact: '钱七', createdAt: '', updatedAt: '' }
    devDepts.value = [dept1, dept2, dept3]

    const fse1: FSE = { id: 1, name: 'FSE-张明', pduId: 1, pduName: 'PDU-研发一部', createdAt: '', updatedAt: '' }
    const fse2: FSE = { id: 2, name: 'FSE-李华', pduId: 2, pduName: 'PDU-研发二部', createdAt: '', updatedAt: '' }
    fses.value = [fse1, fse2]

    const tf1: OrganizationUnit = { id: 1, name: '试验田-A组', type: 'testField', parentId: null, createdAt: '', updatedAt: '' }
    const tf2: OrganizationUnit = { id: 2, name: '试验田-B组', type: 'testField', parentId: null, createdAt: '', updatedAt: '' }
    testFields.value = [tf1, tf2]

    const today = new Date()
    const dates: string[] = []
    for (let i = 0; i < 15; i++) {
      const d = new Date(today.getTime() - (14 - i) * 24 * 60 * 60 * 1000)
      dates.push(d.toISOString().split('T')[0])
    }

    const persons: Personnel[] = [
      { id: 1, employeeNo: 'E001', name: '王小明', pduId: 1, pduName: 'PDU-研发一部', devDeptId: 1, devDeptName: '前端开发组', pduContact: '张三', devContact: '王五', zones: [{ zone: 'blue', modelPermission: 'GPT-4', toolPermission: 'CodeAgent', batchDate: '2024-01-15' }, { zone: 'green', modelPermission: 'Claude-3', toolPermission: 'CodeReview', batchDate: '2024-02-01' }], createdAt: '', updatedAt: '' },
      { id: 2, employeeNo: 'E002', name: '李小红', pduId: 1, pduName: 'PDU-研发一部', devDeptId: 2, devDeptName: '后端开发组', pduContact: '张三', devContact: '赵六', zones: [{ zone: 'blue', modelPermission: 'GPT-4', toolPermission: 'CodeAgent', batchDate: '2024-01-20' }], createdAt: '', updatedAt: '' },
      { id: 3, employeeNo: 'E003', name: '张小刚', pduId: 2, pduName: 'PDU-研发二部', devDeptId: 3, devDeptName: '移动开发组', pduContact: '李四', devContact: '钱七', zones: [{ zone: 'yellow', modelPermission: 'Gemini', toolPermission: 'CodeAgent', batchDate: '2024-02-10' }], createdAt: '', updatedAt: '' },
      { id: 4, employeeNo: 'E004', name: '陈小芳', pduId: 1, pduName: 'PDU-研发一部', devDeptId: 1, devDeptName: '前端开发组', testFieldId: 1, testFieldName: '试验田-A组', fse: 'FSE-张明', zones: [{ zone: 'blue', modelPermission: 'GPT-4', toolPermission: 'CodeAgent', batchDate: '2024-01-25' }], createdAt: '', updatedAt: '' },
      { id: 5, employeeNo: 'E005', name: '赵小强', pduId: 2, pduName: 'PDU-研发二部', devDeptId: 3, devDeptName: '移动开发组', testFieldId: 2, testFieldName: '试验田-B组', fse: 'FSE-李华', zones: [], createdAt: '', updatedAt: '' },
    ]
    personnelList.value = persons

    const usages: DailyUsage[] = []
    let usageId = 1
    persons.forEach(person => {
      dates.forEach((date, dayIndex) => {
        const callCount = Math.floor(Math.random() * 150)
        if (callCount > 0) {
          usages.push({ id: usageId++, personnelId: person.id, employeeNo: person.employeeNo, name: person.name, date, callCount, usedCodeAgent: true })
        }
      })
    })
    dailyUsage.value = usages
  }

  initMockData()

  const getPduById = (id: number) => pdus.value.find(p => p.id === id)
  const getDevDeptById = (id: number) => devDepts.value.find(d => d.id === id)
  const getTestFieldById = (id: number) => testFields.value.find(t => t.id === id)
  const getFseByPduId = (pduId: number) => fses.value.find(f => f.pduId === pduId)

  const getDevDeptsByPdu = (pduId: number) => devDepts.value.filter(d => d.parentId === pduId)

  function addPdu(pdu: Omit<OrganizationUnit, 'id' | 'createdAt' | 'updatedAt'>) {
    const newPdu: OrganizationUnit = {
      ...pdu,
      id: Date.now(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    pdus.value.push(newPdu)
    addAuditLog('create', `新增PDU: ${pdu.name}`)
    return newPdu
  }

  function updatePdu(id: number, pdu: Partial<OrganizationUnit>) {
    const index = pdus.value.findIndex(p => p.id === id)
    if (index !== -1) {
      pdus.value[index] = { ...pdus.value[index], ...pdu, updatedAt: new Date().toISOString() }
      addAuditLog('update', `更新PDU: ${pdus.value[index].name}`)
    }
  }

  function deletePdu(id: number) {
    const pdu = pdus.value.find(p => p.id === id)
    if (pdu) {
      pdus.value = pdus.value.filter(p => p.id !== id)
      devDepts.value = devDepts.value.filter(d => d.parentId !== id)
      fses.value = fses.value.filter(f => f.pduId !== id)
      addAuditLog('delete', `删除PDU: ${pdu.name}`)
    }
  }

  function addDevDept(devDept: Omit<OrganizationUnit, 'id' | 'createdAt' | 'updatedAt'>) {
    const newDevDept: OrganizationUnit = {
      ...devDept,
      id: Date.now(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    devDepts.value.push(newDevDept)
    addAuditLog('create', `新增开发部: ${devDept.name}`)
    return newDevDept
  }

  function updateDevDept(id: number, devDept: Partial<OrganizationUnit>) {
    const index = devDepts.value.findIndex(d => d.id === id)
    if (index !== -1) {
      devDepts.value[index] = { ...devDepts.value[index], ...devDept, updatedAt: new Date().toISOString() }
      addAuditLog('update', `更新开发部: ${devDepts.value[index].name}`)
    }
  }

  function deleteDevDept(id: number) {
    const devDept = devDepts.value.find(d => d.id === id)
    if (devDept) {
      devDepts.value = devDepts.value.filter(d => d.id !== id)
      addAuditLog('delete', `删除开发部: ${devDept.name}`)
    }
  }

  function addFse(fse: Omit<FSE, 'id' | 'createdAt' | 'updatedAt'>) {
    const newFse: FSE = {
      ...fse,
      id: Date.now(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    fses.value.push(newFse)
    addAuditLog('create', `新增FSE: ${fse.name}(负责${fse.pduName})`)
    return newFse
  }

  function updateFse(id: number, fse: Partial<FSE>) {
    const index = fses.value.findIndex(f => f.id === id)
    if (index !== -1) {
      fses.value[index] = { ...fses.value[index], ...fse, updatedAt: new Date().toISOString() }
      addAuditLog('update', `更新FSE: ${fses.value[index].name}`)
    }
  }

  function deleteFse(id: number) {
    const fse = fses.value.find(f => f.id === id)
    if (fse) {
      fses.value = fses.value.filter(f => f.id !== id)
      addAuditLog('delete', `删除FSE: ${fse.name}`)
    }
  }

  function addTestField(field: Omit<OrganizationUnit, 'id' | 'createdAt' | 'updatedAt'>) {
    const newField: OrganizationUnit = {
      ...field,
      id: Date.now(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    testFields.value.push(newField)
    addAuditLog('create', `新增试验田: ${field.name}`)
    return newField
  }

  function updateTestField(id: number, field: Partial<OrganizationUnit>) {
    const index = testFields.value.findIndex(t => t.id === id)
    if (index !== -1) {
      testFields.value[index] = { ...testFields.value[index], ...field, updatedAt: new Date().toISOString() }
      addAuditLog('update', `更新试验田: ${testFields.value[index].name}`)
    }
  }

  function deleteTestField(id: number) {
    const field = testFields.value.find(t => t.id === id)
    if (field) {
      testFields.value = testFields.value.filter(t => t.id !== id)
      addAuditLog('delete', `删除试验田: ${field.name}`)
    }
  }

  function addPersonnel(person: Omit<Personnel, 'id' | 'createdAt' | 'updatedAt'>) {
    const newPerson: Personnel = {
      ...person,
      id: Date.now(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    personnelList.value.push(newPerson)
    addAuditLog('create', `新增人员: ${person.name}(${person.employeeNo})`)
    return newPerson
  }

  function updatePersonnel(id: number, person: Partial<Personnel>) {
    const index = personnelList.value.findIndex(p => p.id === id)
    if (index !== -1) {
      const oldName = personnelList.value[index].name
      personnelList.value[index] = { ...personnelList.value[index], ...person, updatedAt: new Date().toISOString() }
      addAuditLog('update', `更新人员: ${oldName}`)
    }
  }

  function deletePersonnel(id: number) {
    const person = personnelList.value.find(p => p.id === id)
    if (person) {
      personnelList.value = personnelList.value.filter(p => p.id !== id)
      addAuditLog('delete', `删除人员: ${person.name}(${person.employeeNo})`)
    }
  }

  function batchImportPersonnel(persons: Omit<Personnel, 'id' | 'createdAt' | 'updatedAt'>[]) {
    const newPersons = persons.map(person => ({
      ...person,
      id: Date.now() + Math.random(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }))
    personnelList.value.push(...newPersons)
    addAuditLog('import', `批量导入${persons.length}名人员`)
  }

  function batchUpdatePermissions(employeeNos: string[], zones: PersonnelZone[]) {
    let updatedCount = 0
    employeeNos.forEach(empNo => {
      const person = personnelList.value.find(p => p.employeeNo === empNo)
      if (person) {
        const newZones = [...person.zones]
        zones.forEach(zone => {
          const existIndex = newZones.findIndex(z => z.zone === zone.zone)
          if (existIndex >= 0) {
            newZones[existIndex] = zone
          } else {
            newZones.push(zone)
          }
        })
        person.zones = newZones
        person.updatedAt = new Date().toISOString()
        updatedCount++
      }
    })
    addAuditLog('batch_permission', `批量配置权限: ${employeeNos.length}人, ${zones.length}个区域`)
    return updatedCount
  }

  function addDailyUsage(usage: Omit<DailyUsage, 'id'>[]) {
    const newUsage = usage.map(u => ({
      ...u,
      id: Date.now() + Math.random()
    }))
    dailyUsage.value.push(...newUsage)
  }

  function addAuditLog(action: string, detail: string, operator = 'admin', operatorName = '管理员') {
    const log: AuditLog = {
      id: Date.now(),
      action,
      operator,
      operatorName,
      target: '人员管理系统',
      detail,
      createdAt: new Date().toISOString()
    }
    auditLogs.value.unshift(log)
  }

  function getUsageSummary(): UsageSummary {
    const totalPersonnel = personnelList.value.length
    const hasPermissionCount = personnelList.value.filter(p => p.zones.length > 0).length
    const usedCount = new Set(dailyUsage.value.filter(u => u.usedCodeAgent).map(u => u.personnelId)).size

    const personUsageMap = new Map<number, number>()
    dailyUsage.value.forEach(u => {
      const count = personUsageMap.get(u.personnelId) || 0
      personUsageMap.set(u.personnelId, count + u.callCount)
    })

    const topUserCount = [...personUsageMap.entries()].filter(([_, count]) => count >= 100).length

    const personDaysMap = new Map<number, Set<string>>()
    dailyUsage.value.forEach(u => {
      const days = personDaysMap.get(u.personnelId) || new Set()
      days.add(u.date)
      personDaysMap.set(u.personnelId, days)
    })
    const seniorUserCount = [...personDaysMap.entries()].filter(([_, days]) => days.size >= 10).length

    const pduMap = new Map<string, { total: number; hasPermission: number; used: number; top: number; senior: number }>()
    personnelList.value.filter(p => p.pduName).forEach(p => {
      const stat = pduMap.get(p.pduName!) || { total: 0, hasPermission: 0, used: 0, top: 0, senior: 0 }
      stat.total++
      if (p.zones.length > 0) stat.hasPermission++
      pduMap.set(p.pduName!, stat)
    })

    const devDeptMap = new Map<string, { total: number; hasPermission: number; used: number; top: number; senior: number }>()
    personnelList.value.filter(p => p.devDeptName).forEach(p => {
      const stat = devDeptMap.get(p.devDeptName!) || { total: 0, hasPermission: 0, used: 0, top: 0, senior: 0 }
      stat.total++
      if (p.zones.length > 0) stat.hasPermission++
      devDeptMap.set(p.devDeptName!, stat)
    })

    const testFieldMap = new Map<string, { total: number; hasPermission: number; used: number; top: number; senior: number }>()
    personnelList.value.filter(p => p.testFieldName).forEach(p => {
      const stat = testFieldMap.get(p.testFieldName!) || { total: 0, hasPermission: 0, used: 0, top: 0, senior: 0 }
      stat.total++
      if (p.zones.length > 0) stat.hasPermission++
      testFieldMap.set(p.testFieldName!, stat)
    })

    dailyUsage.value.forEach(u => {
      const person = personnelList.value.find(p => p.id === u.personnelId)
      if (person && u.usedCodeAgent) {
        if (person.pduName) {
          const stat = pduMap.get(person.pduName)
          if (stat) stat.used++
        }
        if (person.devDeptName) {
          const stat = devDeptMap.get(person.devDeptName)
          if (stat) stat.used++
        }
        if (person.testFieldName) {
          const stat = testFieldMap.get(person.testFieldName)
          if (stat) stat.used++
        }
      }
    })

    return {
      totalPersonnel,
      hasPermissionCount,
      usedCount,
      topUserCount,
      seniorUserCount,
      byPdu: [...pduMap.entries()].map(([pduName, stat]) => ({ pduName, ...stat })),
      byDevDept: [...devDeptMap.entries()].map(([devDeptName, stat]) => ({ devDeptName, ...stat })),
      byTestField: [...testFieldMap.entries()].map(([testFieldName, stat]) => ({ testFieldName, ...stat }))
    }
  }

  return {
    pdus,
    devDepts,
    fses,
    testFields,
    personnelList,
    dailyUsage,
    auditLogs,
    getPduById,
    getDevDeptById,
    getTestFieldById,
    getFseByPduId,
    getDevDeptsByPdu,
    addPdu,
    updatePdu,
    deletePdu,
    addDevDept,
    updateDevDept,
    deleteDevDept,
    addFse,
    updateFse,
    deleteFse,
    addTestField,
    updateTestField,
    deleteTestField,
    addPersonnel,
    updatePersonnel,
    deletePersonnel,
    batchImportPersonnel,
    batchUpdatePermissions,
    addDailyUsage,
    addAuditLog,
    getUsageSummary
  }
})