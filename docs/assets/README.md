# 文档配图目录

将截图放入对应子目录后，`vibe-coding-timeline.md` 中的图片链接即可正常显示。

## 目录说明

| 目录 | 用途 |
|------|------|
| `agent/` | Cursor 里与 Agent 的对话、改代码、终端输出等过程截图 |
| `app/` | 系统运行后的 Web 界面效果截图 |

## 建议文件名（与正文占位一致）

### `agent/` — 开发过程

| 文件名 | 建议内容 |
|--------|----------|
| `01-feasibility-chat.png` | 首轮需求：Agent 输出可行性 / 数据分层分析 |
| `02-menu-skeleton-prompt.png` | 「先只做主菜单」类提示词与 Agent 回复 |
| `03-menu-skeleton-result.png` | 菜单架子跑起来后的侧边栏 + 占位页 |
| `04-simplify-dept-prompt.png` | 「部门树只要层级和名字」等纠正对话 |
| `05-mysql-connect.png` | 对接 MySQL / 去 Mock 相关对话或终端 |
| `06-charts-prompt.png` | 权限饼图 / 使用统计图需求描述 |
| `07-auth-discuss.png` | 登录鉴权方案讨论 |
| `08-expertise-rollback.png` | （可选）专家经验 DOM 方案与回退 |

### `app/` — 运行效果

| 文件名 | 建议内容 |
|--------|----------|
| `01-login.png` | 登录页 |
| `02-layout-menu.png` | 登录后总览：侧栏 + 各模块入口 |
| `03-config-dept-tree.png` | 配置中心 · 组织架构 / 部门树 |
| `04-config-personnel.png` | 配置中心 · 人员名单（含表头筛选） |
| `05-config-zone-yellow.png` | 黄区白名单 Tab |
| `06-config-zone-stats.png` | 权限统计图弹窗（饼图 + 部门树） |
| `07-usage-table.png` | 使用统计 · 数据明细 + 导入 |
| `08-usage-charts.png` | 使用统计 · 统计图表 Tab |
| `09-placeholder-module.png` | （可选）12345 / 优秀实践占位页 |

## 格式建议

- 格式：PNG 或 WebP，宽度 1200～1600px 为宜（过长可裁切）
- 敏感信息：工号、姓名、内网地址请打码后再放入仓库或发帖副本
