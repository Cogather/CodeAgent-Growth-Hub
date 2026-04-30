import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AccessRequest, UsageStats, Ticket, Artifact, RequestStatus } from '@/types'

export const useMockDataStore = defineStore('mockData', () => {
  const accessRequests = ref<AccessRequest[]>([
    {
      id: 1,
      requestNo: 'AF-20260402-0001',
      zone: 'yellow',
      tool: 'Cursor',
      model: 'GPT-4',
      status: 'processing',
      submitter: '10001',
      submitterName: '张三',
      createdAt: '2026-04-02 10:00:00',
      updatedAt: '2026-04-02 14:00:00',
      processor: 'admin',
      remark: '处理中',
      accounts: [
        { id: 1, requestId: 1, username: '10001', status: 'processing' },
        { id: 2, requestId: 1, username: '10002', status: 'pending' }
      ]
    },
    {
      id: 2,
      requestNo: 'AF-20260401-0003',
      zone: 'blue',
      tool: 'Windsurf',
      model: 'Claude-3',
      status: 'completed',
      submitter: '10003',
      submitterName: '李四',
      createdAt: '2026-04-01 09:00:00',
      updatedAt: '2026-04-01 16:00:00',
      processor: 'admin',
      accounts: [
        { id: 3, requestId: 2, username: '10003', status: 'completed' }
      ]
    },
    {
      id: 3,
      requestNo: 'AF-20260402-0002',
      zone: 'green',
      tool: 'Copilot',
      model: 'GPT-4',
      status: 'pending',
      submitter: '10004',
      submitterName: '王五',
      createdAt: '2026-04-02 11:30:00',
      updatedAt: '2026-04-02 11:30:00',
      accounts: [
        { id: 4, requestId: 3, username: '10004', status: 'pending' },
        { id: 5, requestId: 3, username: '10005', status: 'pending' }
      ]
    }
  ])

  const usageStats = ref<UsageStats[]>([
    { id: 1, username: '10001', name: '张三', department: '研发部', zone: 'yellow', tool: 'Cursor', callCount: 1500, activeDays: 25, isDeepUser: true, date: '2026-04' },
    { id: 2, username: '10002', name: '李四', department: '研发部', zone: 'yellow', tool: 'Cursor', callCount: 800, activeDays: 18, isDeepUser: true, date: '2026-04' },
    { id: 3, username: '10003', name: '王五', department: '测试部', zone: 'blue', tool: 'Windsurf', callCount: 1200, activeDays: 22, isDeepUser: true, date: '2026-04' },
    { id: 4, username: '10004', name: '赵六', department: '产品部', zone: 'green', tool: 'Copilot', callCount: 300, activeDays: 10, isDeepUser: false, date: '2026-04' },
    { id: 5, username: '10005', name: '钱七', department: '研发部', zone: 'yellow', tool: 'Cursor', callCount: 2000, activeDays: 28, isDeepUser: true, date: '2026-04' },
    { id: 6, username: '10006', name: '孙八', department: '设计部', zone: 'blue', tool: 'Windsurf', callCount: 500, activeDays: 15, isDeepUser: false, date: '2026-04' },
    { id: 7, username: '10007', name: '周九', department: '运维部', zone: 'green', tool: 'Copilot', callCount: 450, activeDays: 12, isDeepUser: false, date: '2026-04' },
    { id: 8, username: '10008', name: '吴十', department: '研发部', zone: 'yellow', tool: 'Cursor', callCount: 1800, activeDays: 26, isDeepUser: true, date: '2026-04' }
  ])

  const tickets = ref<Ticket[]>([
    { id: 1, ticketNo: 'TICKET-001', title: 'Cursor无法连接网络', category: 'bug', status: 'resolved', submitter: '10001', submitterName: '张三', processor: 'admin', processorName: '管理员', department: '研发部', link: 'https://jira.example.com/1', createdAt: '2026-03-20 10:00:00', updatedAt: '2026-03-21 15:00:00' },
    { id: 2, ticketNo: 'TICKET-002', title: '请求添加新模型支持', category: 'feature', status: 'processing', submitter: '10002', submitterName: '李四', processor: 'admin', processorName: '管理员', department: '测试部', link: 'https://jira.example.com/2', createdAt: '2026-03-22 14:00:00', updatedAt: '2026-03-25 09:00:00' },
    { id: 3, ticketNo: 'TICKET-003', title: '如何使用API调用', category: 'question', status: 'closed', submitter: '10003', submitterName: '王五', processor: 'admin', processorName: '管理员', department: '产品部', link: 'https://jira.example.com/3', createdAt: '2026-03-25 16:00:00', updatedAt: '2026-03-26 10:00:00' },
    { id: 4, ticketNo: 'TICKET-004', title: '性能优化建议', category: 'optimization', status: 'pending', submitter: '10004', submitterName: '赵六', processor: '', processorName: '', department: '设计部', link: 'https://jira.example.com/4', createdAt: '2026-03-28 11:00:00', updatedAt: '2026-03-28 11:00:00' },
    { id: 5, ticketNo: 'TICKET-005', title: 'Windsurf卡顿问题', category: 'bug', status: 'processing', submitter: '10005', submitterName: '钱七', processor: 'admin', processorName: '管理员', department: '研发部', link: 'https://jira.example.com/5', createdAt: '2026-03-29 09:00:00', updatedAt: '2026-04-01 14:00:00' }
  ])

  const artifacts = ref<Artifact[]>([
    { id: 1, name: 'Cursor高效开发技巧', description: '分享Cursor使用技巧和最佳实践', link: 'https://wiki.example.com/1', publisher: '10001', publisherName: '张三', publisherDept: '研发部', category: 'skill', createdAt: '2026-03-15' },
    { id: 2, name: 'MCP服务器部署指南', description: 'MCP服务器快速部署教程', link: 'https://wiki.example.com/2', publisher: '10002', publisherName: '李四', publisherDept: '测试部', category: 'mcp', createdAt: '2026-03-18' },
    { id: 3, name: 'AI辅助代码审查实践', description: '团队代码审查AI辅助最佳实践', link: 'https://wiki.example.com/3', publisher: '10003', publisherName: '王五', publisherDept: '研发部', category: 'bestpractice', createdAt: '2026-03-20' },
    { id: 4, name: 'Windsurf插件开发', description: 'Windsurf自定义插件开发教程', link: 'https://wiki.example.com/4', publisher: '10004', publisherName: '赵六', publisherDept: '产品部', category: 'skill', createdAt: '2026-03-22' }
  ])

  const tools = ref(['Cursor', 'Windsurf', 'Copilot', 'Claude Code'])
  const models = ref(['GPT-4', 'GPT-4o', 'Claude-3', 'Claude-3.5'])

  const departments = ref([
    { id: 1, name: '研发部', parentId: null },
    { id: 2, name: '测试部', parentId: null },
    { id: 3, name: '产品部', parentId: null },
    { id: 4, name: '设计部', parentId: null },
    { id: 5, name: '运维部', parentId: null },
    { id: 6, name: '前端组', parentId: 1 },
    { id: 7, name: '后端组', parentId: 1 }
  ])

  const deepUserRule = ref({
    callCountThreshold: 500,
    activeDaysThreshold: 15,
    daysWindow: 30
  })

  const addAccessRequest = (req: Omit<AccessRequest, 'id' | 'requestNo' | 'createdAt' | 'updatedAt'>) => {
    const id = accessRequests.value.length + 1
    const requestNo = `AF-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${String(id).padStart(4, '0')}`
    const now = new Date().toISOString().replace('T', ' ').slice(0, 19)
    accessRequests.value.unshift({
      ...req,
      id,
      requestNo,
      createdAt: now,
      updatedAt: now
    })
  }

  const updateAccessRequestStatus = (id: number, status: RequestStatus, remark?: string) => {
    const req = accessRequests.value.find(r => r.id === id)
    if (req) {
      req.status = status
      req.updatedAt = new Date().toISOString().replace('T', ' ').slice(0, 19)
      if (remark) req.remark = remark
      if (status === 'processing') req.processor = 'admin'
    }
  }

  return {
    accessRequests,
    usageStats,
    tickets,
    artifacts,
    tools,
    models,
    departments,
    deepUserRule,
    addAccessRequest,
    updateAccessRequestStatus
  }
})
