# 电解液原材料价格看板

## 项目简介
这是一个电解液原材料价格的可视化看板，支持40种材料的多维度筛选、价格走势对比和数据下载。

## 技术栈
- **框架**: Streamlit
- **图表**: ECharts (via streamlit-echarts)
- **数据**: Supabase / 本地CSV文件
- **数据处理**: Pandas

## 文件夹结构
```
price_dashboard/
├── app.py                       ← Streamlit 入口（根目录，用于Cloud部署）
├── 01_Build/
│   ├── app.py                   ← 主应用：三页面路由、UI渲染
│   ├── data_loader.py           ← 数据加载模块
│   ├── data_cleaner.py          ← 数据清洗：宽表转长表
│   └── utils.py                 ← 工具函数：价格格式化、汇率换算
├── 02_Output/
│   ├── price_data_long.csv      ← 清洗后的长表数据
│   ├── design_preview_0629_v2.html ← UI设计原型
│   ├── 启动看板.bat             ← Windows启动脚本
│   └── 更新数据.bat             ← 数据更新脚本
├── .streamlit/
│   ├── config.toml              ← Streamlit配置
│   └── secrets.toml             ← Supabase密钥（不上传Git）
├── requirements.txt             ← Python依赖
├── PROJECT.md                   ← 架构约定
├── CONTEXT.md                   ← 业务规则
└── README.md                    ← 项目说明
```

## 页面功能
### 1. 总览 · 产业链
- 三列布局：上游原材料、中游电解液/LFP/CNT、下游电芯
- 显示本周均价、环比变化、同比变化

### 2. 单材料价格
- 材料筛选（含 VC-有色网、VC-百川两个数据源）
- 日期范围选择 + 快捷标签（近1周/月/6月/年）
- 频率切换（日度/周度/月度/年度）
- 货币切换（CNY/USD，汇率7.24）
- KPI卡片：最新价格、本周/本月/本年均价
- ECharts折线图 + 数据下载

### 3. 多材料对比
- 模式切换：单Y轴 / 双Y轴 / 归一化
- 材料选择器（支持添加）
- 货币切换（CNY/USD）
- ECharts多线对比图 + 数据下载

## 如何启动
### 方式一：使用启动脚本（推荐）
1. 进入 `02_Output/` 文件夹
2. 双击 `启动看板.bat`

### 方式二：命令行启动
```bash
cd price_dashboard
pip install -r requirements.txt
streamlit run 01_Build/app.py
```

## 数据说明
- 来源：百川盈孚（BaiInfo）、上海有色网（SMM）、GEO内部
- 材料：40种，分8组
- 更新频率：每周更新一次

## 注意事项
- 不要手动修改 `00_Inbox/` 里的文件
- 更新数据时放入新文件即可，文件名建议包含日期后缀
- Supabase 连接信息存放在 `.streamlit/secrets.toml`，不上传Git

## 更新日志

### 2026-06-29
- ✅ 完成 UI 重构，使用 ECharts 替换 Plotly
- ✅ 实现三页面布局：总览、单材料价格、多材料对比
- ✅ 添加材料筛选（含 VC 双数据源：有色网、百川）
- ✅ 添加货币切换（CNY/USD，汇率7.24）
- ✅ 添加数据下载功能，移除明细表
- ✅ 更新 PROJECT.md 和 README.md
- ⚠️ Supabase 连接问题待解决（计划0630处理）