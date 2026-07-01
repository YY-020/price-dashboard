<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>锂电材料价格看板 · 设计原型</title>
    <!-- 使用 ECharts CDN -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js">
    </script>
    <style>
        /* ===== 全局重置 & 字体 ===== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: #0a0a1a;
            color: #e2e8f0;
            height: 100vh;
            display: flex;
            overflow: hidden;
        }
        /* 等宽数字字体 */
        .num {
            font-family: 'JetBrains Mono', 'SF Mono', monospace;
        }

        /* ===== 左侧边栏 ===== */
        .sidebar {
            width: 220px;
            background: #111128;
            border-right: 1px solid #1e293b;
            display: flex;
            flex-direction: column;
            padding: 24px 0 20px 0;
            flex-shrink: 0;
            height: 100vh;
            overflow-y: auto;
        }
        .sidebar .logo {
            padding: 0 20px 32px 20px;
            font-size: 18px;
            font-weight: 700;
            color: #fff;
            letter-spacing: 1px;
        }
        .sidebar .logo span {
            color: #4361ee;
        }
        .sidebar .nav-item {
            padding: 12px 20px;
            margin: 2px 12px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
            color: #94a3b8;
            transition: all 0.2s;
        }
        .sidebar .nav-item:hover {
            background: #1e293b;
            color: #e2e8f0;
        }
        .sidebar .nav-item.active {
            background: #16213e;
            color: #4361ee;
            border-left: 3px solid #4361ee;
            border-radius: 8px 0 0 8px;
            margin-right: 0;
        }
        .sidebar .nav-item .icon {
            font-size: 18px;
            width: 24px;
            text-align: center;
        }
        .sidebar .nav-divider {
            height: 1px;
            background: #1e293b;
            margin: 16px 20px;
        }
        .sidebar .sub-item {
            padding-left: 52px;
            font-size: 13px;
            color: #64748b;
        }
        .sidebar .sub-item.active {
            color: #e2e8f0;
            border-left: none;
            background: transparent;
        }

        /* ===== 右侧主内容 ===== */
        .main {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 20px 28px 28px 28px;
            overflow-y: auto;
            height: 100vh;
            background: #0a0a1a;
        }

        /* 顶部操作栏 */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            flex-shrink: 0;
        }
        .top-bar .page-title {
            font-size: 20px;
            font-weight: 600;
        }
        .top-bar .actions {
            display: flex;
            gap: 16px;
            align-items: center;
        }
        .top-bar .lang-switch {
            background: #16213e;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            color: #94a3b8;
            cursor: pointer;
            border: 1px solid #1e293b;
        }
        .top-bar .lang-switch.active {
            color: #fff;
            border-color: #4361ee;
        }

        /* ===== 页面容器 ===== */
        .page-container {
            flex: 1;
            display: none;
            flex-direction: column;
            gap: 20px;
        }
        .page-container.active {
            display: flex;
        }

        /* ===== KPI 卡片行 ===== */
        .kpi-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            flex-shrink: 0;
        }
        .kpi-card {
            background: #16213e;
            border-radius: 10px;
            padding: 18px 20px;
            border: 1px solid #1e293b;
            transition: all 0.2s;
        }
        .kpi-card:hover {
            border-color: #4361ee;
        }
        .kpi-card .label {
            font-size: 13px;
            color: #94a3b8;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
        }
        .kpi-card .value {
            font-size: 26px;
            font-weight: 700;
            color: #fff;
            letter-spacing: 0.5px;
        }
        .kpi-card .value .unit {
            font-size: 14px;
            font-weight: 400;
            color: #94a3b8;
            margin-left: 6px;
        }
        .kpi-card .change {
            font-size: 14px;
            margin-top: 6px;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .kpi-card .change.up {
            color: #ef4444;
        }
        .kpi-card .change.down {
            color: #22c55e;
        }
        .kpi-card .mini-chart {
            width: 80px;
            height: 30px;
            display: inline-block;
        }

        /* ===== 筛选栏 ===== */
        .filter-bar {
            background: #111128;
            border-radius: 10px;
            padding: 14px 20px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px 20px;
            border: 1px solid #1e293b;
            flex-shrink: 0;
        }
        .filter-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .filter-group label {
            font-size: 13px;
            color: #94a3b8;
            white-space: nowrap;
        }
        .filter-group select,
        .filter-group input {
            background: #0a0a1a;
            border: 1px solid #1e293b;
            border-radius: 6px;
            padding: 6px 12px;
            color: #e2e8f0;
            font-size: 13px;
            outline: none;
        }
        .filter-group select:focus,
        .filter-group input:focus {
            border-color: #4361ee;
        }
        .quick-tags {
            display: flex;
            gap: 6px;
            margin-left: auto;
            flex-wrap: wrap;
        }
        .quick-tags .tag {
            padding: 4px 14px;
            border-radius: 16px;
            background: #0a0a1a;
            border: 1px solid #1e293b;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
            color: #94a3b8;
        }
        .quick-tags .tag:hover {
            border-color: #4361ee;
            color: #fff;
        }
        .quick-tags .tag.active {
            background: #4361ee;
            border-color: #4361ee;
            color: #fff;
        }

        /* ===== 图表容器 ===== */
        .chart-wrapper {
            background: #111128;
            border-radius: 10px;
            padding: 16px 20px 8px 20px;
            border: 1px solid #1e293b;
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 420px;
        }
        .chart-wrapper .chart-title {
            font-size: 14px;
            font-weight: 500;
            color: #94a3b8;
            margin-bottom: 8px;
        }
        .chart-container {
            flex: 1;
            width: 100%;
            min-height: 360px;
        }

        /* ===== 多材料对比页特殊样式 ===== */
        .view-tabs {
            display: flex;
            gap: 4px;
            background: #0a0a1a;
            padding: 4px;
            border-radius: 8px;
            border: 1px solid #1e293b;
            flex-shrink: 0;
        }
        .view-tabs .vt {
            padding: 6px 16px;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            color: #94a3b8;
            transition: all 0.2s;
        }
        .view-tabs .vt.active {
            background: #4361ee;
            color: #fff;
        }
        .view-tabs .vt:hover:not(.active) {
            background: #16213e;
            color: #e2e8f0;
        }

        .material-selector {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }
        .material-selector .pill {
            background: #16213e;
            padding: 4px 12px 4px 16px;
            border-radius: 16px;
            border: 1px solid #1e293b;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .material-selector .pill .dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }
        .material-selector .pill .remove {
            cursor: pointer;
            color: #64748b;
            font-weight: bold;
        }
        .material-selector .add-btn {
            background: transparent;
            border: 1px dashed #1e293b;
            padding: 4px 16px;
            border-radius: 16px;
            color: #94a3b8;
            cursor: pointer;
            font-size: 13px;
        }

        /* ===== 总览页卡片网格 ===== */
        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 16px;
            flex-shrink: 0;
        }
        .overview-card {
            background: #16213e;
            border-radius: 10px;
            padding: 16px;
            border: 1px solid #1e293b;
        }
        .overview-card .mat-name {
            font-size: 14px;
            color: #94a3b8;
        }
        .overview-card .mat-price {
            font-size: 22px;
            font-weight: 700;
            margin: 6px 0 4px;
        }
        .overview-card .mat-change {
            font-size: 13px;
        }
        .overview-card .mat-change.up {
            color: #ef4444;
        }
        .overview-card .mat-change.down {
            color: #22c55e;
        }

        /* ===== 隐藏辅助 ===== */
        .hidden {
            display: none !important;
        }

        /* ===== 滚动条美化 ===== */
        ::-webkit-scrollbar {
            width: 4px;
        }
        ::-webkit-scrollbar-track {
            background: #0a0a1a;
        }
        ::-webkit-scrollbar-thumb {
            background: #1e293b;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #4361ee;
        }

        /* ===== 响应式微调 ===== */
        @media (max-width: 1200px) {
            .kpi-row {
                grid-template-columns: repeat(2, 1fr);
            }
            .sidebar {
                width: 180px;
            }
        }
        @media (max-width: 768px) {
            .sidebar {
                display: none;
            }
            .kpi-row {
                grid-template-columns: 1fr;
            }
            .filter-bar {
                flex-direction: column;
                align-items: stretch;
            }
            .quick-tags {
                margin-left: 0;
            }
        }
    </style>
</head>
<body>

    <!-- ========================================= -->
    <!-- 左侧边栏 -->
    <!-- ========================================= -->
    <div class="sidebar">
        <div class="logo">⛁ <span>Li</span>Price</div>

        <div class="nav-item active" data-page="overview">
            <span class="icon">📊</span> 总览
        </div>
        <div class="nav-item" data-page="price-db">
            <span class="icon">💰</span> 价格数据库
        </div>
        <div class="nav-divider"></div>
        <div style="padding: 0 20px; font-size: 12px; color: #475569; margin-top: 8px;">扩展模块</div>
        <div class="nav-item" style="opacity: 0.5; cursor: not-allowed;">
            <span class="icon">📦</span> 供应追踪
        </div>
        <div class="nav-item" style="opacity: 0.5; cursor: not-allowed;">
            <span class="icon">📈</span> 需求分析
        </div>
    </div>

    <!-- ========================================= -->
    <!-- 右侧主内容 -->
    <!-- ========================================= -->
    <div class="main">

        <!-- 顶部栏 -->
        <div class="top-bar">
            <div class="page-title" id="pageTitle">📊 总览</div>
            <div class="actions">
                <span class="lang-switch active">CN</span>
                <span class="lang-switch">EN</span>
                <span style="width: 32px; height: 32px; background: #4361ee; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; cursor: pointer;">B</span>
            </div>
        </div>

        <!-- ========================================= -->
        <!-- 页面1：总览 (Overview) -->
        <!-- ========================================= -->
        <div class="page-container active" id="page-overview">
            <div class="overview-grid" id="overviewGrid">
                <!-- JS 动态渲染 -->
            </div>
            <div style="margin-top: 20px; background: #111128; border-radius: 10px; padding: 20px; border: 1px solid #1e293b; flex:1; min-height:200px; display:flex; align-items:center; justify-content:center; color:#475569; font-size:14px;">
                📌 快速概览：今日所有材料价格快照 (点击材料可跳转详情)
            </div>
        </div>

        <!-- ========================================= -->
        <!-- 页面2：价格数据库 -->
        <!-- ========================================= -->
        <div class="page-container" id="page-price-db">

            <!-- Tab 切换：单材料 / 多材料 -->
            <div style="display: flex; gap: 0; border-bottom: 2px solid #1e293b; margin-bottom: 20px; flex-shrink: 0;">
                <div class="db-tab active" data-tab="single" style="padding: 10px 24px; cursor: pointer; font-weight: 500; border-bottom: 3px solid #4361ee; color: #fff;">单材料价格信息</div>
                <div class="db-tab" data-tab="multi" style="padding: 10px 24px; cursor: pointer; font-weight: 500; border-bottom: 3px solid transparent; color: #94a3b8;">多材料对比</div>
            </div>

            <!-- ======== Tab 1: 单材料 ======== -->
            <div id="subtab-single" class="subtab-content" style="display: flex; flex-direction: column; gap: 20px; flex:1;">
                <!-- KPI 卡片 -->
                <div class="kpi-row" id="singleKpi">
                    <div class="kpi-card">
                        <div class="label">最新价格 <span>电池级碳酸锂</span></div>
                        <div class="value">147,500 <span class="unit">元/吨</span></div>
                        <div class="change up">▲ +2.3% <span style="color:#94a3b8; font-weight:400; margin-left:6px;">vs 上周</span></div>
                    </div>
                    <div class="kpi-card">
                        <div class="label">周度涨跌幅</div>
                        <div class="value" style="color:#ef4444;">+2.3%</div>
                        <div class="change up">↑ 1.2% <span style="color:#94a3b8; font-weight:400; margin-left:6px;">vs 上月</span></div>
                    </div>
                    <div class="kpi-card">
                        <div class="label">月度涨跌幅</div>
                        <div class="value" style="color:#22c55e;">-5.1%</div>
                        <div class="change down">↓ 3.2% <span style="color:#94a3b8; font-weight:400; margin-left:6px;">vs 季初</span></div>
                    </div>
                    <div class="kpi-card">
                        <div class="label">年度涨跌幅</div>
                        <div class="value" style="color:#ef4444;">+18.7%</div>
                        <div class="change up">↑ 18.7% <span style="color:#94a3b8; font-weight:400; margin-left:6px;">vs 去年今日</span></div>
                    </div>
                </div>

                <!-- 筛选栏 -->
                <div class="filter-bar">
                    <div class="filter-group">
                        <label>材料</label>
                        <select>
                            <option>电池级碳酸锂</option>
                            <option>六氟磷酸锂</option>
                            <option>电解液溶剂 DMC</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>开始</label>
                        <input type="date" value="2023-06-26" />
                    </div>
                    <div class="filter-group">
                        <label>结束</label>
                        <input type="date" value="2026-06-26" />
                    </div>
                    <div class="filter-group">
                        <label>频率</label>
                        <select><option>日度</option><option>周度</option><option>月度</option></select>
                    </div>
                    <div class="quick-tags">
                        <span class="tag">近1周</span>
                        <span class="tag">近1月</span>
                        <span class="tag active">近6月</span>
                        <span class="tag">近1年</span>
                        <span class="tag">近3年</span>
                        <span class="tag">全部</span>
                    </div>
                </div>

                <!-- 图表 -->
                <div class="chart-wrapper" style="flex:1;">
                    <div class="chart-title">电池级碳酸锂 日度价格 2023-06-26 至 2026-06-26（元/吨）</div>
                    <div id="singleChart" class="chart-container"></div>
                    <div style="font-size: 12px; color: #475569; margin-top: 4px;">数据来源：SMM / GEO / BaiInfor</div>
                </div>
            </div>

            <!-- ======== Tab 2: 多材料 ======== -->
            <div id="subtab-multi" class="subtab-content" style="display: none; flex-direction: column; gap: 20px; flex:1;">

                <!-- 多材料筛选 + 视图切换 -->
                <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px; background: #111128; padding: 14px 20px; border-radius: 10px; border: 1px solid #1e293b;">
                    <div class="material-selector">
                        <span style="color:#94a3b8; font-size:13px;">对比材料：</span>
                        <span class="pill"><span class="dot" style="background:#4361ee;"></span> 碳酸锂 <span class="remove">×</span></span>
                        <span class="pill"><span class="dot" style="background:#06d6a0;"></span> 六氟磷酸锂 <span class="remove">×</span></span>
                        <span class="pill"><span class="dot" style="background:#ffd166;"></span> 电解液 DMC <span class="remove">×</span></span>
                        <span class="add-btn">+ 添加材料 (最多5种)</span>
                    </div>
                    <div class="view-tabs">
                        <span class="vt active" data-view="normalized">归一化</span>
                        <span class="vt" data-view="dual">双Y轴</span>
                        <span class="vt" data-view="facet">分面图</span>
                    </div>
                </div>

                <!-- 图表容器 -->
                <div class="chart-wrapper" style="flex:1;">
                    <div class="chart-title">多材料价格对比 (归一化至起始日100%)</div>
                    <div id="multiChart" class="chart-container"></div>
                    <div style="font-size: 12px; color: #475569; margin-top: 4px;">数据来源：SMM / GEO / BaiInfor</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // =============================================
        // 1. 导航切换 (侧边栏)
        // =============================================
        const navItems = document.querySelectorAll('.nav-item[data-page]');
        const pages = {
            overview: document.getElementById('page-overview'),
            'price-db': document.getElementById('page-price-db')
        };
        const pageTitle = document.getElementById('pageTitle');

        navItems.forEach(item => {
            item.addEventListener('click', function() {
                navItems.forEach(n => n.classList.remove('active'));
                this.classList.add('active');
                const page = this.dataset.page;
                Object.keys(pages).forEach(key => {
                    pages[key].classList.toggle('active', key === page);
                });
                pageTitle.textContent = page === 'overview' ? '📊 总览' : '💰 价格数据库';
                // 触发图表resize
                setTimeout(() => {
                    if (window.singleChart) window.singleChart.resize();
                    if (window.multiChart) window.multiChart.resize();
                }, 100);
            });
        });

        // =============================================
        // 2. 价格数据库内部 Tab 切换 (单/多)
        // =============================================
        const dbTabs = document.querySelectorAll('.db-tab');
        const subtabs = {
            single: document.getElementById('subtab-single'),
            multi: document.getElementById('subtab-multi')
        };

        dbTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                dbTabs.forEach(t => {
                    t.classList.remove('active');
                    t.style.borderBottomColor = 'transparent';
                    t.style.color = '#94a3b8';
                });
                this.classList.add('active');
                this.style.borderBottomColor = '#4361ee';
                this.style.color = '#fff';

                const target = this.dataset.tab;
                Object.keys(subtabs).forEach(key => {
                    subtabs[key].style.display = (key === target) ? 'flex' : 'none';
                });

                // resize charts after toggle
                setTimeout(() => {
                    if (window.singleChart) window.singleChart.resize();
                    if (window.multiChart) window.multiChart.resize();
                }, 200);
            });
        });

        // =============================================
        // 3. 多材料视图切换 (归一化/双Y/分面)
        // =============================================
        const viewTabs = document.querySelectorAll('.vt');
        viewTabs.forEach(vt => {
            vt.addEventListener('click', function() {
                viewTabs.forEach(v => v.classList.remove('active'));
                this.classList.add('active');
                // 实际项目这里切换图表配置，此处我们只改变标题提示以展示交互
                const title = document.querySelector('#subtab-multi .chart-title');
                const mode = this.textContent.trim();
                title.textContent = `多材料价格对比 (${mode}模式)`;
                // 模拟切换图表数据 (实际开发需重新渲染)
                if (window.multiChart) {
                    // 简单演示：改变颜色或提示，实际项目中根据模式调整option
                    console.log(`切换至 ${mode} 模式`);
                    // 为演示效果，重新设置一个随机波动 (仅展示交互)
                    const option = window.multiChart.getOption();
                    // 这里为了演示，只做一个resize触发展示，不重构数据
                    window.multiChart.resize();
                }
            });
        });

        // =============================================
        // 4. 渲染总览页 (简单汇总)
        // =============================================
        const overviewData = [
            { name: '电池级碳酸锂', price: '147,500', change: '+2.3%', status: 'up' },
            { name: '六氟磷酸锂', price: '68,200', change: '-1.2%', status: 'down' },
            { name: '电解液 DMC', price: '12,450', change: '+0.8%', status: 'up' },
            { name: '电解液 EMC', price: '18,300', change: '+4.5%', status: 'up' },
            { name: '磷酸铁锂', price: '43,200', change: '-2.1%', status: 'down' },
            { name: '碳纳米管', price: '92,800', change: '+0.3%', status: 'up' },
        ];

        const grid = document.getElementById('overviewGrid');
        overviewData.forEach(item => {
            const card = document.createElement('div');
            card.className = 'overview-card';
            card.innerHTML = `
                        <div class="mat-name">${item.name}</div>
                        <div class="mat-price num">${item.price}</div>
                        <div class="mat-change ${item.status}">${item.status === 'up' ? '▲' : '▼'} ${item.change}</div>
                    `;
            // 点击跳转到价格数据库 (演示)
            card.style.cursor = 'pointer';
            card.addEventListener('click', () => {
                document.querySelector('.nav-item[data-page="price-db"]').click();
            });
            grid.appendChild(card);
        });

        // =============================================
        // 5. ECharts 图表渲染
        // =============================================
        // 5.1 单材料图表 (面积图)
        const singleChart = echarts.init(document.getElementById('singleChart'));
        window.singleChart = singleChart;

        // 生成模拟数据 (2023-06-26 到 2026-06-26)
        const dates = [];
        const prices = [];
        let start = new Date('2023-06-26');
        const end = new Date('2026-06-26');
        let current = new Date(start);
        while (current <= end) {
            dates.push(current.toISOString().slice(0, 10));
            // 模拟价格波动
            const base = 150000;
            const trend = (current - start) / (end - start) * 20000; // 上涨趋势
            const noise = (Math.random() - 0.5) * 40000;
            prices.push(Math.round(base + trend + noise));
            current.setMonth(current.getMonth() + 1); // 每月一个点
        }

        const singleOption = {
            tooltip: {
                trigger: 'axis',
                backgroundColor: '#16213e',
                borderColor: '#1e293b',
                textStyle: { color: '#e2e8f0' },
                formatter: function(params) {
                    const p = params[0];
                    return `<strong>${p.axisValue}</strong><br/>价格：<strong>${p.value.toLocaleString()}</strong> 元/吨`;
                }
            },
            grid: {
                left: '4%',
                right: '4%',
                bottom: '8%',
                top: '6%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: dates,
                axisLine: { lineStyle: { color: '#1e293b' } },
                axisLabel: { color: '#94a3b8', fontSize: 11 },
                splitLine: { show: false },
                axisTick: { show: false }
            },
            yAxis: {
                type: 'value',
                splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } },
                axisLabel: { color: '#94a3b8', fontSize: 11, formatter: function(v) { return (v / 10000) + '万'; } },
                name: '元/吨',
                nameTextStyle: { color: '#94a3b8', fontSize: 11 }
            },
            series: [{
                data: prices,
                type: 'line',
                smooth: true,
                symbol: 'circle',
                symbolSize: 4,
                lineStyle: {
                    color: '#4361ee',
                    width: 2
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(67, 97, 238, 0.4)' },
                        { offset: 1, color: 'rgba(67, 97, 238, 0.02)' }
                    ])
                },
                markPoint: {
                    data: [
                        { type: 'max', name: '最大值', symbolSize: 48 },
                        { type: 'min', name: '最小值', symbolSize: 48 }
                    ],
                    label: {
                        color: '#e2e8f0',
                        formatter: function(params) {
                            return params.value.toLocaleString();
                        },
                        fontSize: 10,
                        position: 'top'
                    }
                },
                markLine: {
                    silent: true,
                    data: [
                        { yAxis: prices[prices.length - 1], name: '最新价' }
                    ],
                    label: {
                        color: '#22c55e',
                        formatter: '最新 {c}',
                        fontSize: 10
                    }
                }
            }]
        };
        singleChart.setOption(singleOption);

        // 5.2 多材料图表 (归一化对比)
        const multiChart = echarts.init(document.getElementById('multiChart'));
        window.multiChart = multiChart;

        // 生成3条模拟曲线 (归一化)
        const multiDates = dates;
        const materials = ['碳酸锂', '六氟磷酸锂', '电解液 DMC'];
        const colors = ['#4361ee', '#06d6a0', '#ffd166'];
        const seriesData = materials.map((name, idx) => {
            const base = 100;
            const trend = (idx + 1) * 15;
            const data = prices.map((p, i) => {
                const factor = 1 + (i / prices.length) * (idx + 1) * 0.3;
                const noise = (Math.random() - 0.5) * 10;
                return Math.round(base + trend + (i / prices.length) * 40 + noise);
            });
            return {
                name: name,
                type: 'line',
                smooth: true,
                symbol: 'circle',
                symbolSize: 4,
                lineStyle: { width: 2 },
                data: data,
                itemStyle: { color: colors[idx] }
            };
        });

        const multiOption = {
            tooltip: {
                trigger: 'axis',
                backgroundColor: '#16213e',
                borderColor: '#1e293b',
                textStyle: { color: '#e2e8f0' },
                formatter: function(params) {
                    let html = `<strong>${params[0].axisValue}</strong><br/>`;
                    params.forEach(p => {
                        html +=
                            `${p.marker} ${p.seriesName}: <strong>${p.value.toFixed(1)}%</strong><br/>`;
                    });
                    return html;
                }
            },
            legend: {
                data: materials,
                textStyle: { color: '#94a3b8' },
                top: 0,
                right: 0,
                icon: 'circle',
                itemWidth: 10,
                itemHeight: 10
            },
            grid: {
                left: '4%',
                right: '4%',
                bottom: '8%',
                top: '14%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: multiDates,
                axisLine: { lineStyle: { color: '#1e293b' } },
                axisLabel: { color: '#94a3b8', fontSize: 10, interval: 10 },
                splitLine: { show: false }
            },
            yAxis: {
                type: 'value',
                min: 80,
                max: 180,
                splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } },
                axisLabel: { color: '#94a3b8', fontSize: 11, formatter: '{value}%' },
                name: '归一化价格指数',
                nameTextStyle: { color: '#94a3b8', fontSize: 11 }
            },
            series: seriesData
        };
        multiChart.setOption(multiOption);

        // =============================================
        // 6. 窗口自适应
        // =============================================
        window.addEventListener('resize', function() {
            if (window.singleChart) window.singleChart.resize();
            if (window.multiChart) window.multiChart.resize();
        });

        // 切换多材料视图时重新渲染（模拟更新数据）
        // 实际项目中，这里根据view模式更新option，这里仅做演示，增加响应
        console.log('✅ 锂电价格看板设计原型已加载');
        console.log('📌 交互提示：点击侧边栏切换页面，点击"多材料对比"内的视图切换按钮可查看模式切换。');
    </script>

</body>
</html>