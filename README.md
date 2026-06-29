# 电解液原材料价格看板

## 项目简介
这是一个电解液原材料价格的可视化看板，支持40种材料的多维度筛选、价格走势对比和数据明细查询。

## 文件夹结构
price_dashboard/
├── app.py                       ← 唯一入口：只做页面路由和登录状态管理
├── config/
│   └── constants.py             ← 全局常量：材料分组、颜色策略、图表默认值
├── core/
│   ├── auth.py                  ← 登录验证、管理员权限判断、用户管理
│   ├── database.py              ← 和Supabase交互：查询数据、上传数据、更新数据
│   └── data_processor.py        ← 数据处理：宽表↔长表转换、价格格式化、单位处理
├── pages/
│   ├── overview.py              ← 总览页：所有材料今日价格快照
│   ├── detail.py                ← 单材料详情页：单个材料的KPI卡片+折线图
│   ├── compare.py               ← 多材料对比页：选择最多5个材料，叠加折线图
│   └── upload.py                ← 管理员上传页：上传Excel → 自动入库
├── components/
│   ├── sidebar.py               ← 侧边栏：材料分组选择器、时间范围、频率切换
│   ├── charts.py                ← 图表组件：折线图、KPI卡片、数据表格
│   └── ui_helpers.py            ← UI工具：颜色映射、格式统一、中文化
├── 00_Inbox/                    ← 原始Excel文件存放（不上传Git）
├── 02_Output/                   ← 输出文件（不上传Git）
├── requirements.txt             ← Python依赖
├── .gitignore                   ← Git排除规则
├── README.md                    ← 项目说明（给人看）
├── PROJECT.md                   ← 架构约定（给AI看）
├── CONTEXT.md                   ← 业务规则（给AI看）
└── SYSTEM.md                    ← 技术配置（本地留存，不上传Git）

## 如何启动
1. 确认 `00_Inbox/` 里有最新版本的价格文件（命名格式为 `price_data_日期.xlsx`，如 `price_data_0513.xlsx`）
2. 进入 `02_Output/`，双击 `启动看板.bat`（或AI生成的启动文件）
3. 浏览器自动打开看板页面

## 数据说明
- 来源：百川盈孚（BaiInfo）、上海有色网（SMM）、GEO内部
- 材料：40种，分10组
- 更新频率：每周更新一次，新数据插入Excel最顶部

## 注意事项
- 不要手动修改 `00_Inbox/` 里的文件
- 更新数据时放入新文件即可，文件名建议包含日期后缀方便版本管理
- 旧版本价格文件可以移到 `_DOCS/` 存档，不要留在 `00_Inbox/` 里干扰AI读取