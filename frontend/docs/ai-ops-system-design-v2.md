# AI辅助研发运营系统设计文档 v2（需求收敛版）

## 1. 产品定位

一个服务于“AI辅助研发提效”活动的运营中台，核心目标：

- 把线下收集名单、跟进进展、维护Excel的工作迁移到线上；
- 统一管理**权限申请流、问题单分析、使用数据分析、产出看护**；
- 对不同角色做严格权限控制，确保信息可见范围符合管理要求。

---

## 2. 技术栈（前后端分离）

- 前端：`Vue 3 + TypeScript + Vite + Element Plus + Pinia + ECharts`
- 后端：`FastAPI + SQLAlchemy + PostgreSQL + Redis + Celery`
- 文件导入导出：`openpyxl/pandas`
- 鉴权与权限：`SSO/JWT + RBAC + 数据域权限`
- 部署：`Docker`（后续可上K8s）

---

## 3. 角色与权限

### 3.1 角色定义

系统共四个角色：

| 角色 | 标识 | 说明 |
|------|------|------|
| 管理员 | `admin` | 系统最高权限，负责审批电子流、管理用户、查看全量数据 |
| FSE | `fse` | 可提交权限申请、查看自己的电子流、查看使用数据看板 |
| PDU接口人 | `pdu` | 可提交权限申请、查看自己的电子流、查看使用数据看板 |
| 一线支撑 | `support` | 可提交权限申请、查看自己的电子流 |

### 3.2 功能权限矩阵

| 功能 | 管理员 | FSE | PDU接口人 | 一线支撑 |
|------|:------:|:---:|:---------:|:--------:|
| 提交权限申请（单个/批量） | ✓ | ✓ | ✓ | ✓ |
| 查看自己的电子流 | ✓ | ✓ | ✓ | ✓ |
| 管理员审批处理池 | ✓ | — | — | — |
| 使用数据看板（全量） | ✓ | ✓ | ✓ | — |
| 使用数据导出 | ✓ | — | — | — |
| 问题单分析页 | ✓ | — | — | — |
| 产出看护录入/管理 | ✓ | — | — | — |
| 系统管理 | ✓ | — | — | — |

### 3.3 关键权限说明

- **审批处理池**：仅管理员可见，其他角色不展示该菜单
- **导出能力**：仅管理员可导出（使用数据、电子流人员、问题单）
- **12345服务单分析**：仅管理员可访问
- **系统管理**：仅管理员可访问
- FSE / PDU接口人 可查看使用数据看板，但不能导出
- 一线支撑仅能操作权限申请相关功能

---

## 4. 功能模块设计

## 模块A：权限申请与电子流管理（重点）

### A.1 提交申请

任何已登录用户均可发起申请，支持两种模式：

#### 单账号申请

表单字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| 工号 | 文本输入 | 必填，格式校验（如：6位数字） |
| 网络区域 | 单选 | 黄 / 蓝 / 绿，必选 |
| 模型 | 单选/多选 | 从字典表读取，必选 |
| IDE | 多选 | VSCode / JetBrains，必选 |
| 工具类别 | 多选 | 从字典表读取，必选 |
| 申请说明 | 文本域 | 选填，最多200字 |

#### 批量申请

- 页面顶部展示一个**大文本框**，提示语：`请输入工号，多个工号用英文逗号分隔，格式示例：100001,100002,100003`
- 文本框下方实时解析预览：显示”已识别 N 个工号 / 无效 M 个”
- 无效工号高亮标红，鼠标悬停提示原因（格式错误 / 重复）
- 工号区域下方与单账号申请相同，统一选择：**网络区域、模型、IDE、工具类别**
- 所有字段均为必填，校验通过后方可提交

批量校验规则：
1. 自动去除空格、换行，以英文逗号为分隔符解析
2. 格式校验：仅允许纯数字工号（长度6位）
3. 去重：同一批次内重复工号自动合并，提示用户
4. 上限：单次批量提交不超过 200 个工号

### A.2 电子流机制

提交后系统自动生成电子流，规则如下：

**单号规则**：`AF-{YYYYMMDD}-{4位序号}`，如 `AF-20260402-0001`

**状态流转**：

```
待受理 → 处理中 → 已完成
              ↘ 已驳回
```

- `待受理`：用户提交后默认状态
- `处理中`：管理员点击”受理”后流转
- `已完成`：管理员点击”审批通过”后流转，电子流结束
- `已驳回`：管理员点击”驳回”并填写原因后流转，电子流结束

**用户侧**：
- 提交后可在”我的电子流”页面查看所有本人提交的记录
- 可查看每条电子流的：单号、提交时间、当前状态、处理人、处理时间、驳回原因（如有）
- 电子流详情页展示该批次内所有工号的处理状态

**管理员侧**：
- 登录后首页/工作台展示”待办”数量角标
- 进入”管理员处理池”可看到所有待受理/处理中的电子流列表
- 点击某条电子流可查看详情，包含提交人信息、工号明细列表
- 操作按钮：**受理 / 审批通过 / 驳回**
- 驳回时必须填写驳回原因（必填，最多200字）
- 审批通过后电子流状态自动变为”已完成”

### A.3 管理员工作台

**列表筛选条件**：

- 电子流单号（模糊搜索）
- 提交人工号 / 姓名
- 网络区域（黄/蓝/绿）
- 工具类别
- 模型
- IDE
- 状态（待受理/处理中/已完成/已驳回）
- 提交时间范围

**批量操作**：

- 勾选多条电子流 → 批量受理
- 勾选多条电子流 → 批量审批通过
- 每批操作支持填写统一备注

**进度统计看板**（页面顶部）：

- 总申请数 / 待受理数 / 处理中数 / 已完成数 / 已驳回数
- 本周新增 / 本周完成

### A.4 导出功能（管理员专属）

支持将电子流中的人员信息导出为 Excel，两种方式：

1. **单条导出**：在电子流详情页点击”导出本单人员”
2. **批量导出**：在列表页勾选多条电子流后点击”批量导出人员”

导出的 Excel 包含以下列：

| 列名 | 说明 |
|------|------|
| 电子流单号 | 如 AF-20260402-0001 |
| 提交人姓名 | 发起申请的用户姓名 |
| 提交人工号 | 发起申请的用户工号 |
| 申请人工号 | 被申请开通权限的工号（批量时每行一个） |
| 申请人姓名 | 对应工号的姓名（如系统内有则填充） |
| 申请人部门 | 对应工号的部门 |
| 网络区域 | 黄/蓝/绿 |
| 模型 | 申请的模型名称 |
| IDE | VSCode / JetBrains |
| 工具类别 | 申请的工具类别 |
| 申请时间 | 电子流提交时间 |
| 审批时间 | 电子流完成时间 |
| 状态 | 当前电子流状态 |

导出行为记录审计日志（操作人、时间、导出范围、导出条数）。

---

## 模块B：问题单处理情况（仅管理员）

### B.1 列表与过滤

过滤维度：

- 部门（支持多级部门）
- 单子类别
- 处理进度/状态

展示字段：

- 单号
- 提交人
- 当前处理人
- 状态
- 提交时间
- 链接

### B.2 导出

- 支持当前筛选结果导出Excel
- 导出行为记录审计日志（谁在何时导出了什么范围）

---

## 模块C：用户使用数据看板

### C.1 页面布局

**顶部区域切换**：
- 固定 Tab 切换：`黄区 / 蓝区 / 绿区`
- 切换 Tab 后，下方所有数据（筛选器、列表、统计）自动刷新为对应区域数据

**筛选器区域**（位于 Tab 下方）：

| 筛选项 | 类型 | 说明 |
|--------|------|------|
| 工具类别 | 多选下拉 | 从字典表读取，支持全选/反选 |
| 部门 | 级联选择器 | 支持多级部门树选择，可选择父级或叶子节点 |
| 时间区间 | 日期范围选择器 | 默认最近30天，支持自定义起止日期 |

筛选器右侧操作按钮：
- **查询**：应用筛选条件刷新列表
- **重置**：清空所有筛选条件
- **导出 Excel**：导出当前筛选结果（管理员专属）

### C.2 人员明细列表

表格列定义：

| 列名 | 字段说明 | 数据来源 | 排序 |
|------|----------|----------|------|
| 工号 | 用户工号 | users.employee_id | 支持 |
| 姓名 | 用户姓名 | users.name | 支持 |
| 部门 | 所属部门全路径 | departments.path 拼接 | 支持 |
| 累计调用次数 | 时间区间内总调用量 | SUM(usage_stats_daily.call_count) | 支持，默认降序 |
| 最大连续使用天数 | 时间区间内最长连续活跃天数 | 计算逻辑见下方 | 支持 |
| 是否 TOP 用户 | 是/否标识 | 根据系统配置规则动态判定 | 支持筛选 |

**列表交互**：
- 默认按“累计调用次数”降序排列
- 支持点击列头切换升序/降序
- 分页展示，每页 20/50/100 条可选
- 列表顶部显示统计：`共 X 人，其中 TOP 用户 Y 人`

### C.3 最大连续使用天数计算逻辑

基于 `usage_stats_daily` 表中的 `stat_date` 字段：

1. 筛选出当前用户在指定时间区间、网络区域、工具类别下的所有活跃日期
2. 按日期升序排列，计算日期间隔
3. 如果相邻两天日期差 = 1，则视为连续
4. 统计所有连续段，取最大值

**SQL 示例**（PostgreSQL）：

```sql
WITH user_dates AS (
    SELECT DISTINCT stat_date
    FROM usage_stats_daily
    WHERE employee_id = '100001'
      AND network_zone = 'yellow'
      AND tool_code IN ('tool1', 'tool2')
      AND stat_date BETWEEN '2026-03-01' AND '2026-03-31'
    ORDER BY stat_date
),
date_groups AS (
    SELECT
        stat_date,
        stat_date - (ROW_NUMBER() OVER (ORDER BY stat_date))::INT AS grp
    FROM user_dates
)
SELECT MAX(cnt) AS max_consecutive_days
FROM (
    SELECT grp, COUNT(*) AS cnt
    FROM date_groups
    GROUP BY grp
) t;
```

### C.4 TOP 用户判定规则

**系统配置表**（可在“系统管理 - TOP 用户规则”页面修改）：

```sql
CREATE TABLE top_user_rules (
    id                      SERIAL PRIMARY KEY,
    min_call_count          INT NOT NULL DEFAULT 100,
    min_consecutive_days    INT NOT NULL DEFAULT 7,
    is_active               BOOLEAN DEFAULT TRUE,
    updated_by              INT REFERENCES users(id),
    updated_at              TIMESTAMP DEFAULT NOW()
);
```

**判定逻辑**：

用户在当前筛选条件下（时间区间、网络区域、工具类别）满足以下两个条件时，标记为 TOP 用户：

1. `累计调用次数 >= min_call_count`
2. `最大连续使用天数 >= min_consecutive_days`

### C.5 导出功能

点击“导出 Excel”按钮后，导出当前筛选结果，Excel 列与页面列表完全一致：

| Excel 列名 | 对应字段 |
|-----------|---------|
| 工号 | employee_id |
| 姓名 | name |
| 部门 | department_path |
| 累计调用次数 | total_call_count |
| 最大连续使用天数 | max_consecutive_days |
| 是否 TOP 用户 | is_top_user（是/否） |

**导出文件命名规则**：
`用户使用数据_{网络区域}_{YYYYMMDD_HHmmss}.xlsx`

**导出行为审计**：
- 记录到 `audit_logs` 表
- 包含：操作人、导出时间、网络区域、工具类别、部门、时间区间、导出行数

---

## 模块D：自动图表与高阶分析

系统自动生成基础图表：

1. **按部门排序柱状图**
   - 调用量TOP部门
   - 活跃人数TOP部门

2. **按日期趋势折线图**
   - 每日调用量趋势
   - 每日日活人数趋势（DAU）

3. **可联动过滤**
   - 受区域tab、工具类型、时间范围影响

4. **导出**
   - 图表可下载PNG
   - 图表对应数据可导出Excel

---

## 模块E：Skill/MCP/优秀实践看护（管理员录入）

### E.1 数据来源模式

由于无法自动采集，采用**人工维护**：

- 在线单条新增
- Excel批量导入

### E.2 基础字段

- Name
- 描述
- 链接
- 发布人
- 发布时间
- 类别（Skill / MCP / 优秀实践）
- 发布人所在部门

### E.3 管理功能

- 列表筛选：类别、部门、发布时间
- 去重提醒：name + 链接组合检测
- 导出与审计记录

---

## 5. 信息架构（前端菜单）

- 仪表盘
- 权限申请
  - 我要申请
  - 我的电子流
  - 管理员处理池（管理员）
- 使用数据
  - 黄区
  - 蓝区
  - 绿区
  - 人员明细
- 问题单分析（仅管理员）
- 产出看护（Skill/MCP/优秀实践）
- 系统管理
  - 角色与账号管理
  - 部门管理
  - 字典配置（工具/模型/类别）
  - TOP用户规则
  - 审计日志

---

## 6. 核心数据表设计

### 6.1 用户与组织

```sql
-- 部门表（多级树）
CREATE TABLE departments (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    parent_id   INT REFERENCES departments(id),
    path        VARCHAR(500),           -- 物化路径，如 /1/3/7/
    level       SMALLINT DEFAULT 1,
    sort_order  INT DEFAULT 0,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- 用户表
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    employee_id   VARCHAR(20) NOT NULL UNIQUE,  -- 工号
    name          VARCHAR(50) NOT NULL,
    department_id INT REFERENCES departments(id),
    role          VARCHAR(20) NOT NULL DEFAULT 'fse',  -- admin / fse / pdu / support
    email         VARCHAR(100),
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW()
);
```

### 6.2 字典配置表

```sql
-- 字典表（统一管理工具类别、模型、IDE等枚举值）
CREATE TABLE dict_items (
    id         SERIAL PRIMARY KEY,
    category   VARCHAR(50) NOT NULL,   -- 如：model / tool / ide / network_zone
    code       VARCHAR(50) NOT NULL,
    label      VARCHAR(100) NOT NULL,
    sort_order INT DEFAULT 0,
    is_active  BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (category, code)
);

-- 预置数据示例：
-- ('network_zone', 'yellow', '黄区')
-- ('network_zone', 'blue',   '蓝区')
-- ('network_zone', 'green',  '绿区')
-- ('ide', 'vscode',     'VSCode')
-- ('ide', 'jetbrains',  'JetBrains')
```

### 6.3 权限申请电子流

```sql
-- 电子流主表
CREATE TABLE access_requests (
    id              SERIAL PRIMARY KEY,
    flow_no         VARCHAR(30) NOT NULL UNIQUE,  -- AF-20260402-0001
    submitter_id    INT NOT NULL REFERENCES users(id),  -- 提交人
    network_zone    VARCHAR(20) NOT NULL,          -- yellow / blue / green
    model_codes     VARCHAR(200) NOT NULL,         -- 逗号分隔，如 claude-3,gpt-4
    ide_codes       VARCHAR(100) NOT NULL,         -- 逗号分隔，如 vscode,jetbrains
    tool_codes      VARCHAR(200) NOT NULL,         -- 逗号分隔工具类别code
    remark          TEXT,                          -- 申请说明
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
                                                   -- pending/processing/approved/rejected
    handler_id      INT REFERENCES users(id),      -- 处理人（管理员）
    handled_at      TIMESTAMP,                     -- 处理时间
    reject_reason   TEXT,                          -- 驳回原因
    account_count   INT DEFAULT 0,                 -- 本单工号总数
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_access_requests_submitter ON access_requests(submitter_id);
CREATE INDEX idx_access_requests_status    ON access_requests(status);
CREATE INDEX idx_access_requests_created   ON access_requests(created_at);

-- 电子流工号明细表（每个工号一行）
CREATE TABLE access_request_accounts (
    id              SERIAL PRIMARY KEY,
    request_id      INT NOT NULL REFERENCES access_requests(id) ON DELETE CASCADE,
    employee_id     VARCHAR(20) NOT NULL,   -- 被申请开通的工号
    employee_name   VARCHAR(50),            -- 冗余姓名，提交时从users表查填
    department_id   INT REFERENCES departments(id),  -- 冗余部门
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ara_request_id   ON access_request_accounts(request_id);
CREATE INDEX idx_ara_employee_id  ON access_request_accounts(employee_id);

-- 电子流操作日志（状态变更记录）
CREATE TABLE access_request_logs (
    id          SERIAL PRIMARY KEY,
    request_id  INT NOT NULL REFERENCES access_requests(id) ON DELETE CASCADE,
    operator_id INT NOT NULL REFERENCES users(id),
    action      VARCHAR(30) NOT NULL,  -- submit / accept / approve / reject
    from_status VARCHAR(20),
    to_status   VARCHAR(20),
    comment     TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);
```

### 6.4 使用数据

```sql
-- 每日用户使用数据（按用户+工具+区域聚合，每行代表某用户某天在某区域某工具下的调用记录）
CREATE TABLE usage_stats_daily (
    id            SERIAL PRIMARY KEY,
    stat_date     DATE NOT NULL,
    employee_id   VARCHAR(20) NOT NULL,
    network_zone  VARCHAR(20) NOT NULL,   -- yellow / blue / green
    tool_code     VARCHAR(50) NOT NULL,   -- 工具类别 code，关联 dict_items
    call_count    INT NOT NULL DEFAULT 0, -- 当日调用次数
    department_id INT REFERENCES departments(id),  -- 冗余部门，便于聚合查询
    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW(),
    UNIQUE (stat_date, employee_id, network_zone, tool_code)
);

CREATE INDEX idx_usd_date         ON usage_stats_daily(stat_date);
CREATE INDEX idx_usd_employee     ON usage_stats_daily(employee_id);
CREATE INDEX idx_usd_zone         ON usage_stats_daily(network_zone);
CREATE INDEX idx_usd_tool         ON usage_stats_daily(tool_code);
CREATE INDEX idx_usd_dept         ON usage_stats_daily(department_id);
-- 复合索引，覆盖最常见的查询模式
CREATE INDEX idx_usd_zone_date    ON usage_stats_daily(network_zone, stat_date);
CREATE INDEX idx_usd_emp_zone     ON usage_stats_daily(employee_id, network_zone, stat_date);

-- TOP 用户规则配置表（全局唯一一条有效配置）
CREATE TABLE top_user_rules (
    id                   SERIAL PRIMARY KEY,
    min_call_count       INT NOT NULL DEFAULT 100,  -- 累计调用次数阈值
    min_consecutive_days INT NOT NULL DEFAULT 7,    -- 最大连续使用天数阈值
    is_active            BOOLEAN DEFAULT TRUE,
    updated_by           INT REFERENCES users(id),
    updated_at           TIMESTAMP DEFAULT NOW()
);

-- TOP 用户规则修改历史
CREATE TABLE top_user_rule_logs (
    id                       SERIAL PRIMARY KEY,
    old_min_call_count       INT,
    old_min_consecutive_days INT,
    new_min_call_count       INT,
    new_min_consecutive_days INT,
    operator_id              INT REFERENCES users(id),
    created_at               TIMESTAMP DEFAULT NOW()
);
```

**查询说明**：

`是否 TOP 用户` 为动态计算字段，不落库，每次查询时实时计算：

```sql
-- 查询指定区域+工具+时间区间下的人员明细（含 TOP 用户判定）
WITH rule AS (
    SELECT min_call_count, min_consecutive_days
    FROM top_user_rules WHERE is_active = TRUE LIMIT 1
),
user_stats AS (
    SELECT
        u.employee_id,
        u.name,
        d.name AS department,
        SUM(s.call_count)                          AS total_call_count,
        -- 最大连续使用天数通过子查询或应用层计算（见 C.3）
        0                                          AS max_consecutive_days  -- 占位，实际由应用层填充
    FROM usage_stats_daily s
    JOIN users u ON u.employee_id = s.employee_id
    LEFT JOIN departments d ON d.id = s.department_id
    WHERE s.network_zone = :zone
      AND s.tool_code = ANY(:tool_codes)
      AND s.stat_date BETWEEN :start_date AND :end_date
      AND (:dept_id IS NULL OR s.department_id = :dept_id)
    GROUP BY u.employee_id, u.name, d.name
)
SELECT
    us.*,
    CASE
        WHEN us.total_call_count >= r.min_call_count
         AND us.max_consecutive_days >= r.min_consecutive_days
        THEN '是' ELSE '否'
    END AS is_top_user
FROM user_stats us, rule r
ORDER BY us.total_call_count DESC;
```

> 最大连续使用天数计算较重，建议在应用层（Python）批量计算后合并结果，或使用 PostgreSQL 窗口函数一次性处理所有用户（见 C.3 SQL 示例）。

### 6.5 问题单

```sql
-- 问题单镜像表（从外部系统同步或手工导入）
CREATE TABLE tickets (
    id              SERIAL PRIMARY KEY,
    ticket_no       VARCHAR(50) NOT NULL UNIQUE,
    title           VARCHAR(500),
    submitter_id    INT REFERENCES users(id),
    submitter_name  VARCHAR(50),
    department_id   INT REFERENCES departments(id),
    category        VARCHAR(50),          -- 问题单类别
    status          VARCHAR(30),
    assignee_name   VARCHAR(50),          -- 当前处理人
    submitted_at    TIMESTAMP,
    closed_at       TIMESTAMP,
    source_url      VARCHAR(500),
    synced_at       TIMESTAMP DEFAULT NOW()
);
```

### 6.6 专家经验看护

```sql
-- Skill / MCP / 优秀实践
CREATE TABLE artifacts (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(200) NOT NULL,
    description   TEXT,
    url           VARCHAR(500),
    category      VARCHAR(20) NOT NULL,   -- skill / mcp / practice
    publisher_id  INT REFERENCES users(id),
    publisher_name VARCHAR(50),
    department_id INT REFERENCES departments(id),
    published_at  DATE,
    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW()
);
```

### 6.7 审计日志

```sql
-- 审计日志（导出、审批、状态变更等关键操作）
CREATE TABLE audit_logs (
    id          BIGSERIAL PRIMARY KEY,
    operator_id INT REFERENCES users(id),
    action      VARCHAR(50) NOT NULL,     -- export / approve / reject / import ...
    resource    VARCHAR(50),              -- access_request / ticket / artifact ...
    resource_id VARCHAR(50),
    detail      JSONB,                    -- 导出范围、条数等扩展信息
    ip          VARCHAR(50),
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_operator  ON audit_logs(operator_id);
CREATE INDEX idx_audit_action    ON audit_logs(action);
CREATE INDEX idx_audit_created   ON audit_logs(created_at);
```

### 6.8 表关系总览

```
users ──────────────────────────────────────────────────────┐
  │                                                          │
  ├── access_requests (submitter_id / handler_id)           │
  │       │                                                  │
  │       ├── access_request_accounts (employee_id → users) │
  │       └── access_request_logs (operator_id → users)     │
  │                                                          │
  ├── usage_stats_daily (employee_id)                        │
  ├── tickets (submitter_id)                                 │
  ├── artifacts (publisher_id)                               │
  └── audit_logs (operator_id)                               │
                                                             │
departments ─────────────────────────────────────────────────┘
  (users.department_id / access_request_accounts.department_id
   / tickets.department_id / artifacts.department_id)
```

---

## 7. 关键API示例（节选）

- `POST /api/v1/access-requests` 创建申请（单个/批量）
- `POST /api/v1/access-requests/{id}/batch-process` 管理员分批处理
- `POST /api/v1/access-requests/{id}/close` 自动关闭电子流
- `GET /api/v1/tickets` 问题单筛选查询（管理员）
- `GET /api/v1/tickets/export` 问题单导出（管理员）
- `GET /api/v1/usage/overview?zone=yellow` 分区看板
- `GET /api/v1/usage/users/export` 用户明细导出
- `POST /api/v1/artifacts/import` 批量导入产出
- `POST /api/v1/artifacts` 单条新增产出

---

## 8. 关键交互细节

1. **工号粘贴输入框**
   - 自动分割、去重、格式校验
   - 实时反馈有效数/无效数/重复数

2. **批量处理体验**
   - 管理员勾选后“一键分批”
   - 每批支持备注，便于线下跟进

3. **可见进展**
   - 电子流详情显示：创建时间、当前状态、最近处理动作、处理人

---

## 9. 实施建议（MVP）

MVP建议先做四块：

1. 权限申请电子流（含批量工号粘贴）
2. 使用数据黄蓝绿tab + 人员明细导出
3. 问题单管理员分析页 + 导出
4. 产出看护录入（单条/批量）

---

## 10. 后续迭代建议

- 接入自动数据采集（替代手工导入）
- 增强问题单NLP分类与词云准确率
- 增加部门级运营周报自动订阅推送
- 建设产出复用评价体系（被引用次数、收益跟踪）
