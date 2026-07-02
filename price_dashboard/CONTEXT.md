# 业务背景

## 技术栈

### 前端
- **框架**：原生 HTML5 + CSS3 + JavaScript（ES6+）
- **图表库**：Apache ECharts 5.x（通过CDN引入）
- **数据导出**：XLSX.js（客户端Excel生成）
- **样式**：Tailwind CSS 风格的自定义CSS

### 后端
- **框架**：Streamlit 1.32+
- **语言**：Python 3.10+
- **数据处理**：Pandas 2.2+
- **数据库**：Supabase（PostgreSQL）
- **服务器**：内置HTTP Server（开发环境）/ Streamlit Cloud（生产环境）

### 数据架构
- **数据存储**：Supabase `price_data` 表（长表格式：date, material_key, price）
- **元数据**：本地 `price_data_meta.csv`（单位、数据源、化学式）
- **缓存策略**：Streamlit `@st.cache_data(ttl=300)`，客户端localStorage

### 部署
- **平台**：Streamlit Cloud（免费版）
- **版本控制**：GitHub
- **环境变量**：Streamlit Secrets（Supabase URL/Key）

### 项目结构
```
price_dashboard/
├── app.py                      # Streamlit Cloud入口
├── requirements.txt            # Python依赖
├── .streamlit/config.toml      # Streamlit配置
├── 01_Build/
│   ├── app.py                  # 实际Streamlit应用
│   ├── data_loader.py          # 数据加载模块
│   ├── run_dashboard.py        # 独立HTTP服务器运行脚本
│   └── static/
│       ├── ui_prototype.html   # UI原型（HTML/CSS/JS）
│       ├── dashboard.html      # 生成的看板HTML
│       └── dashboard_data.json # 数据JSON（开发环境）
└── 02_Output/
    ├── price_data_long.csv     # 长表数据（历史备份）
    └── price_data_meta.csv     # 元数据
```

## 项目用途
我是电解液/锂电池行业的市场分析师。这个价格看板用于：
- 我自己快速查看原材料价格走势
- 给领导和同事展示市场变化趋势
- 支撑采购和销售决策

## 数据说明
- 文件：`00_Inbox/price_data_0513.xlsx`（后续可能更新为 price_data_0608.xlsx 等）
- 结构：前7行是表头说明（分类、材料名、规格、CAS编号、单位、数据源、化学式）
- 数据从第8行开始：第1列是日期，后面40列是40种材料的价格
- 单位：RMB/t（电芯是 RMB/Wh，需要特别注意小数点位数）
- 数据源：BaiInfo（百川盈孚）、SMM（上海有色网）、GEO（内部采购）

## 材料分组（10组，共40种）
1. 上游原材料（8种）：乙烯、乙炔、硫酸镍、硫酸钴、硫酸锰、碳酸锂、氢氧化锂·微粉、氢氧化锂·粗颗粒
2. 电解液溶剂（6种）：碳酸乙烯酯EC、碳酸丙烯酯PC、碳酸二甲酯DMC、碳酸甲乙酯EMC、碳酸二乙酯DEC、乙酸甲酯MA
3. 电解液添加剂（6种）：碳酸亚乙烯酯（百川）、碳酸亚乙烯酯（有色网）、氟代碳酸乙烯酯FEC、硫酸乙烯酯DTD、丙烯磺酸内酯PRS、1,3-丙烷磺酸内酯PS
4. 电解液锂盐（5种）：LiFSi·折固、LiFSi·固体、六氟磷酸锂LiFP6、LiDFOB·固体、LiPO2F2·固体
5. 电解液（2种）：三元用、磷酸铁锂用
6. 磷酸铁（1种）
7. 磷酸铁锂（2种）：储能高端型、动力高端型
8. 碳纳米管（6种）：多壁浆料-高端、多壁浆料-低端、多壁粉体-高端、多壁粉体-低端、单壁粉体-高端、单壁粉体-低端
9. NMP（1种）
10. 电芯（3种）：8系三元、方形铁锂储能型、方形铁锂动力型

## 用户习惯
- 用户可能会用中文名或化学式缩写搜索材料，如输入"EC"应匹配"碳酸乙烯酯EC"，输入"LiFP6"应匹配"六氟磷酸锂LiFP6"
- 搜索栏如果无匹配结果，提示"暂未收录该材料价格"
- 用户关心绝对价格变化，不需要太多文字说明

## 样式偏好
- 专业金融风格，类似 Bloomberg/大宗商品研报
- 白色背景，浅灰网格线
- 折线图使用平滑曲线
- 数据标签：大于100的取整数，小于1的保留1-3位小数
- 配色克制，不要花里胡哨

## 数据更新说明
- 价格 Excel 每周更新一次
- 新数据插入到 Excel 最顶部几行
- 看板代码需要自动检测数据区，不要写死行数范围
- 文件命名可能包含日期后缀（如 price_data_0513.xlsx），方便版本管理