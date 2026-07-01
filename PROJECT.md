# 项目协作规则

## 项目目标
这是一个电解液原材料价格看板项目，支持从本地文件或 Supabase 读取价格数据，生成可交互的折线图看板。

## 硬约束（绝对不能做的事）
- 不要修改、删除或重命名 `00_Inbox/` 里的任何文件
- 不要把临时文件放到 `00_Inbox/`
- 不要展示任何真实密钥或密码
- 不要写死数据行数范围，数据每周更新，新数据插入顶部

## 工作方式
- 修改代码前，先说明准备改什么、为什么改
- 修改后做最小验证（至少运行一次确认不报错）
- 如果新增了启动方式或依赖，同步更新 README.md
- 不确定的事标记"待确认"，不要自己猜

## 路径约定
- 输入文件夹：`00_Inbox/`
- 代码文件夹：`01_Build/`
- 输出文件夹：`02_Output/`
- 日志文件夹：`logs/`

## 当前架构
```
price_dashboard/
├── app.py                       ← Streamlit 入口文件（根目录，用于Cloud部署）
├── 01_Build/
│   ├── app.py                   ← 主应用：页面路由、UI渲染
│   ├── data_loader.py           ← 数据加载：本地文件/Supabase读取
│   ├── data_cleaner.py          ← 数据清洗：宽表转长表
│   └── utils.py                 ← 工具函数：价格格式化、汇率换算
├── 02_Output/                   ← 输出文件（清洗后的数据、设计预览）
├── .streamlit/
│   └── secrets.toml             ← Supabase 密钥（不上传Git）
├── requirements.txt             ← Python依赖
├── PROJECT.md                   ← 架构约定（给AI看）
├── CONTEXT.md                   ← 业务规则（给AI看）
└── README.md                    ← 项目说明（给人看）
```

## 常用命令
- 启动看板：`streamlit run 01_Build/app.py`
- 安装依赖：`pip install -r requirements.txt`

## 待办事项
- [ ] 0630：修改 data_loader.py 支持本地文件加载，用于UI测试
- [ ] 0630：解决 Supabase 连接问题
- [ ] 后续：完善多材料对比页的材料删除功能