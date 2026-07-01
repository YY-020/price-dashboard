let MATERIAL_GROUPS = {};
let ALL_MATERIALS = [];
let priceData = [];
let streamlitData = null;

function initStreamlit() {
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/streamlit-component-lib@latest';
    script.onload = function() {
        Streamlit.setComponentReady();
        Streamlit.addOnParametersChanged((params) => {
            if (params) {
                streamlitData = params;
                if (params.materialGroups) {
                    MATERIAL_GROUPS = JSON.parse(params.materialGroups);
                    ALL_MATERIALS = Object.values(MATERIAL_GROUPS).flat();
                }
                if (params.priceData) {
                    priceData = JSON.parse(params.priceData);
                }
                initApp();
            }
        });
    };
    document.head.appendChild(script);
}

function initApp() {
    renderOverview();
    initSinglePage();
    initMultiPage();
}

function getThisWeekRange() {
    const now = new Date();
    const day = now.getDay();
    const monday = new Date(now);
    monday.setDate(now.getDate() - (day === 0 ? 6 : day - 1));
    const friday = new Date(monday);
    friday.setDate(monday.getDate() + 4);
    return {
        start: monday.toISOString().slice(0, 10),
        end: friday.toISOString().slice(0, 10)
    };
}

function getWeeklyAvg(materialKey) {
    const range = getThisWeekRange();
    const filtered = priceData.filter(d =>
        d.material_key === materialKey &&
        d.date >= range.start &&
        d.date <= range.end
    );
    if (filtered.length === 0) return null;
    const sum = filtered.reduce((s, r) => s + r.price, 0);
    return Math.round(sum / filtered.length);
}

function getLatestPrice(materialKey) {
    const filtered = priceData.filter(d => d.material_key === materialKey);
    if (filtered.length === 0) return null;
    filtered.sort((a, b) => b.date.localeCompare(a.date));
    return filtered[0];
}

function getPriceOnDate(materialKey, dateStr) {
    const found = priceData.find(d => d.material_key === materialKey && d.date === dateStr);
    return found ? found.price : null;
}

function calcChange(current, previous) {
    if (!previous || previous === 0) return null;
    return ((current - previous) / previous * 100);
}

function getPeriodAvg(materialKey, dateStr, period) {
    let start, end;
    const d = new Date(dateStr + 'T00:00:00');
    if (period === 'week') {
        const day = d.getDay();
        const mon = new Date(d);
        mon.setDate(d.getDate() - (day === 0 ? 6 : day - 1));
        const sun = new Date(mon);
        sun.setDate(mon.getDate() + 6);
        start = mon.toISOString().slice(0, 10);
        end = sun.toISOString().slice(0, 10);
    } else if (period === 'month') {
        start = dateStr.slice(0, 7) + '-01';
        const lastDay = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();
        end = dateStr.slice(0, 7) + '-' + String(lastDay).padStart(2, '0');
    } else if (period === 'year') {
        start = dateStr.slice(0, 4) + '-01-01';
        end = dateStr.slice(0, 4) + '-12-31';
    } else {
        return null;
    }
    const filtered = priceData.filter(d =>
        d.material_key === materialKey &&
        d.date >= start &&
        d.date <= end
    );
    if (filtered.length === 0) return null;
    const sum = filtered.reduce((s, r) => s + r.price, 0);
    return Math.round(sum / filtered.length);
}

function renderOverview() {
    const grid = document.getElementById('overviewGrid');
    grid.innerHTML = '';

    const colConfigs = [
        { title: '⬆ 上游 · 原材料', keys: ['上游原材料'] },
        { title: '⚙️ 中游 · 电解液 / LFP / CNT', keys: ['电解液溶剂', '电解液添加剂', '电解液锂盐', '电解液', '磷酸铁锂', '碳纳米管'] },
        { title: '⬇ 下游 · 电芯', keys: ['电芯'] },
    ];

    colConfigs.forEach(col => {
        const colDiv = document.createElement('div');
        colDiv.className = 'overview-col';

        const titleDiv = document.createElement('div');
        titleDiv.className = 'col-title';
        titleDiv.innerHTML = `${col.title} <span class="badge">本周均价</span>`;
        colDiv.appendChild(titleDiv);

        const itemsContainer = document.createElement('div');

        col.keys.forEach(groupKey => {
            const materials = MATERIAL_GROUPS[groupKey] || [];
            materials.forEach(mat => {
                const avg = getWeeklyAvg(mat.key);
                const latest = getLatestPrice(mat.key);
                const item = document.createElement('div');
                item.className = 'overview-item';

                const nameSpan = document.createElement('span');
                nameSpan.className = 'mat-name';
                let displayName = mat.label;
                displayName = displayName.replace(/(\d+)/g, (match) => `<sub>${match}</sub>`);
                nameSpan.innerHTML = displayName;

                const priceSpan = document.createElement('span');
                priceSpan.className = 'mat-price';
                const changesSpan = document.createElement('span');
                changesSpan.className = 'mat-changes';

                if (avg !== null && latest) {
                    priceSpan.innerHTML = `${avg} <span class="unit">元/吨</span>`;

                    const lastWeekDate = new Date();
                    lastWeekDate.setDate(lastWeekDate.getDate() - 7);
                    const lastWeekStr = lastWeekDate.toISOString().slice(0, 10);
                    const lastWeekPrice = getPriceOnDate(mat.key, lastWeekStr);
                    const changeWoW = lastWeekPrice ? calcChange(avg, lastWeekPrice) : null;

                    const lastYearDate = new Date();
                    lastYearDate.setFullYear(lastYearDate.getFullYear() - 1);
                    const lastYearStr = lastYearDate.toISOString().slice(0, 10);
                    const lastYearPrice = getPriceOnDate(mat.key, lastYearStr);
                    const changeYoY = lastYearPrice ? calcChange(avg, lastYearPrice) : null;

                    let html = '';
                    if (changeWoW !== null) {
                        const cls = changeWoW > 0.5 ? 'up' : changeWoW < -0.5 ? 'down' : 'flat';
                        const sign = changeWoW > 0 ? '+' : '';
                        html += `<span class="${cls}">${sign}${changeWoW.toFixed(1)}% <span class="label-light">环比</span></span>`;
                    }
                    if (changeYoY !== null) {
                        const cls = changeYoY > 0.5 ? 'up' : changeYoY < -0.5 ? 'down' : 'flat';
                        const sign = changeYoY > 0 ? '+' : '';
                        html += `<span class="${cls}">${sign}${changeYoY.toFixed(1)}% <span class="label-light">同比</span></span>`;
                    }
                    changesSpan.innerHTML = html || '<span class="flat">—</span>';
                } else {
                    priceSpan.innerHTML = '—';
                    changesSpan.innerHTML = '<span class="flat">暂无数据</span>';
                }

                const leftDiv = document.createElement('div');
                leftDiv.style.display = 'flex';
                leftDiv.style.flexDirection = 'column';
                leftDiv.appendChild(nameSpan);
                const rightDiv = document.createElement('div');
                rightDiv.style.display = 'flex';
                rightDiv.style.alignItems = 'center';
                rightDiv.style.gap = '10px';
                rightDiv.appendChild(priceSpan);
                rightDiv.appendChild(changesSpan);

                item.appendChild(leftDiv);
                item.appendChild(rightDiv);
                itemsContainer.appendChild(item);
            });
        });

        colDiv.appendChild(itemsContainer);
        grid.appendChild(colDiv);
    });

    const now = new Date();
    document.getElementById('globalUpdateTime').textContent =
        now.toISOString().slice(0, 10) + ' ' + now.toTimeString().slice(0, 5);
}

let singleChartInstance = null;
let singleCurrentData = [];

function initSinglePage() {
    const select = document.getElementById('singleMaterial');
    select.innerHTML = '';

    Object.keys(MATERIAL_GROUPS).forEach(group => {
        const optgroup = document.createElement('optgroup');
        optgroup.label = group;
        MATERIAL_GROUPS[group].forEach(mat => {
            const opt = document.createElement('option');
            opt.value = mat.key;
            opt.textContent = mat.label;
            optgroup.appendChild(opt);
        });
        select.appendChild(optgroup);
    });

    const firstMat = ALL_MATERIALS[0];
    if (firstMat) select.value = firstMat.key;

    const end = new Date();
    const start = new Date();
    start.setFullYear(start.getFullYear() - 1);
    document.getElementById('singleStart').value = start.toISOString().slice(0, 10);
    document.getElementById('singleEnd').value = end.toISOString().slice(0, 10);

    select.addEventListener('change', updateSingle);
    document.getElementById('singleStart').addEventListener('change', updateSingle);
    document.getElementById('singleEnd').addEventListener('change', updateSingle);
    document.getElementById('singleFreq').addEventListener('change', updateSingle);
    document.getElementById('singleUnit').addEventListener('change', updateSingle);

    document.querySelectorAll('#singleFilterBar .quick-tags .tag').forEach(tag => {
        tag.addEventListener('click', function() {
            document.querySelectorAll('#singleFilterBar .quick-tags .tag').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            const range = this.dataset.range;
            const endDate = new Date();
            let startDate = new Date();
            switch (range) {
                case '7d':
                    startDate.setDate(startDate.getDate() - 7);
                    break;
                case '1m':
                    startDate.setMonth(startDate.getMonth() - 1);
                    break;
                case '6m':
                    startDate.setMonth(startDate.getMonth() - 6);
                    break;
                case '1y':
                    startDate.setFullYear(startDate.getFullYear() - 1);
                    break;
                case 'all':
                    startDate = new Date('2023-01-01');
                    break;
                default:
                    return;
            }
            document.getElementById('singleStart').value = startDate.toISOString().slice(0, 10);
            document.getElementById('singleEnd').value = endDate.toISOString().slice(0, 10);
            updateSingle();
        });
    });

    singleChartInstance = echarts.init(document.getElementById('singleChart'));
    updateSingle();
}

function updateSingle() {
    const materialKey = document.getElementById('singleMaterial').value;
    const startDate = document.getElementById('singleStart').value;
    const endDate = document.getElementById('singleEnd').value;
    const freq = document.getElementById('singleFreq').value;
    const unit = document.getElementById('singleUnit').value;

    let filtered = priceData.filter(d =>
        d.material_key === materialKey &&
        d.date >= startDate &&
        d.date <= endDate
    );
    filtered.sort((a, b) => a.date.localeCompare(b.date));

    let aggregated = filtered;
    if (freq === '周度') aggregated = aggregateByPeriod(filtered, 'week');
    else if (freq === '月度') aggregated = aggregateByPeriod(filtered, 'month');
    else if (freq === '年度') aggregated = aggregateByPeriod(filtered, 'year');

    singleCurrentData = aggregated;

    updateSingleKPI(materialKey, aggregated, unit);
    updateSingleChart(materialKey, aggregated, unit, freq);

    const matLabel = ALL_MATERIALS.find(m => m.key === materialKey)?.label || materialKey;
    document.getElementById('singleChartTitle').textContent =
        `${matLabel} ${freq}价格走势  ${startDate} 至 ${endDate}`;
}

function aggregateByPeriod(data, period) {
    if (data.length === 0) return [];
    const result = [];
    let bucket = [];
    let currentKey = null;
    data.forEach(d => {
        let key;
        if (period === 'week') {
            const dateObj = new Date(d.date + 'T00:00:00');
            const year = dateObj.getFullYear();
            const weekNum = getWeekNumber(dateObj);
            key = `${year}-W${String(weekNum).padStart(2, '0')}`;
        } else if (period === 'month') {
            key = d.date.slice(0, 7);
        } else if (period === 'year') {
            key = d.date.slice(0, 4);
        }
        if (!currentKey) currentKey = key;
        if (key !== currentKey) {
            if (bucket.length > 0) {
                const avg = Math.round(bucket.reduce((s, r) => s + r.price, 0) / bucket.length);
                result.push({ date: bucket[0].date, price: avg });
            }
            bucket = [];
            currentKey = key;
        }
        bucket.push(d);
    });
    if (bucket.length > 0) {
        const avg = Math.round(bucket.reduce((s, r) => s + r.price, 0) / bucket.length);
        result.push({ date: bucket[0].date, price: avg });
    }
    return result;
}

function getWeekNumber(d) {
    const start = new Date(d.getFullYear(), 0, 1);
    const diff = (d - start) / 86400000;
    return Math.ceil((diff + start.getDay() + 1) / 7);
}

function updateSingleKPI(materialKey, data, unit) {
    const container = document.getElementById('singleKpi');
    if (data.length === 0) {
        container.innerHTML =
            '<div class="kpi-card" style="grid-column:1/-1;text-align:center;padding:32px;">暂无数据</div>';
        return;
    }

    const latest = data[data.length - 1];
    const rate = unit === 'CNY' ? 1 : 0.14;
    const latestPrice = Math.round(latest.price * rate);
    const unitLabel = unit === 'CNY' ? '元/吨' : '美元/吨';

    const now = new Date();
    const todayStr = now.toISOString().slice(0, 10);

    const weekAvg = getPeriodAvg(materialKey, todayStr, 'week');
    const lastWeekDate = new Date(now);
    lastWeekDate.setDate(now.getDate() - 7);
    const lastWeekStr = lastWeekDate.toISOString().slice(0, 10);
    const lastWeekAvg = getPeriodAvg(materialKey, lastWeekStr, 'week');
    const changeWeekMom = (weekAvg && lastWeekAvg) ? calcChange(weekAvg, lastWeekAvg) : null;

    const lastYearWeekDate = new Date(now);
    lastYearWeekDate.setFullYear(now.getFullYear() - 1);
    const lastYearWeekStr = lastYearWeekDate.toISOString().slice(0, 10);
    const lastYearWeekAvg = getPeriodAvg(materialKey, lastYearWeekStr, 'week');
    const changeWeekYoy = (weekAvg && lastYearWeekAvg) ? calcChange(weekAvg, lastYearWeekAvg) : null;

    const monthAvg = getPeriodAvg(materialKey, todayStr, 'month');
    const lastMonthDate = new Date(now);
    lastMonthDate.setMonth(now.getMonth() - 1);
    const lastMonthStr = lastMonthDate.toISOString().slice(0, 10);
    const lastMonthAvg = getPeriodAvg(materialKey, lastMonthStr, 'month');
    const changeMonthMom = (monthAvg && lastMonthAvg) ? calcChange(monthAvg, lastMonthAvg) : null;

    const lastYearMonthDate = new Date(now);
    lastYearMonthDate.setFullYear(now.getFullYear() - 1);
    const lastYearMonthStr = lastYearMonthDate.toISOString().slice(0, 10);
    const lastYearMonthAvg = getPeriodAvg(materialKey, lastYearMonthStr, 'month');
    const changeMonthYoy = (monthAvg && lastYearMonthAvg) ? calcChange(monthAvg, lastYearMonthAvg) : null;

    const yearAvg = getPeriodAvg(materialKey, todayStr, 'year');
    const lastYearDate = new Date(now);
    lastYearDate.setFullYear(now.getFullYear() - 1);
    const lastYearStr = lastYearDate.toISOString().slice(0, 10);
    const lastYearAvg = getPeriodAvg(materialKey, lastYearStr, 'year');
    const changeYearMom = (yearAvg && lastYearAvg) ? calcChange(yearAvg, lastYearAvg) : null;

    const twoYearsAgo = new Date(now);
    twoYearsAgo.setFullYear(now.getFullYear() - 2);
    const twoYearsStr = twoYearsAgo.toISOString().slice(0, 10);
    const twoYearsAvg = getPeriodAvg(materialKey, twoYearsStr, 'year');
    const changeYearYoy = (yearAvg && twoYearsAvg) ? calcChange(yearAvg, twoYearsAvg) : null;

    const cards = [{
        label: '最新价格',
        value: latestPrice,
        unit: unitLabel,
        dateTag: latest.date,
        changes: []
    }, {
        label: '周度变化',
        value: null,
        changes: [
            { label: '环比', value: changeWeekMom },
            { label: '同比', value: changeWeekYoy }
        ]
    }, {
        label: '月度变化',
        value: null,
        changes: [
            { label: '环比', value: changeMonthMom },
            { label: '同比', value: changeMonthYoy }
        ]
    }, {
        label: '年度变化',
        value: null,
        changes: [
            { label: '环比', value: changeYearMom },
            { label: '同比', value: changeYearYoy }
        ]
    }];

    container.innerHTML = cards.map(c => {
        let valueHtml = '';
        if (c.value !== null) {
            valueHtml = `<div class="value">${c.value.toLocaleString()} <span class="unit">${c.unit}</span></div>`;
        }
        let changesHtml = '';
        if (c.changes && c.changes.length > 0) {
            changesHtml = '<div class="changes">';
            c.changes.forEach(ch => {
                if (ch.value !== null) {
                    const cls = ch.value > 0.5 ? 'up' : ch.value < -0.5 ? 'down' : 'flat';
                    const sign = ch.value > 0 ? '+' : '';
                    changesHtml += `<span class="item ${cls}">${sign}${ch.value.toFixed(2)}% <span class="label-light">${ch.label}</span></span>`;
                } else {
                    changesHtml += `<span class="item flat">— <span class="label-light">${ch.label}</span></span>`;
                }
            });
            changesHtml += '</div>';
        }
        const dateTagHtml = c.dateTag ? `<span class="date-tag">更新：${c.dateTag}</span>` : '';
        return `<div class="kpi-card"><div class="label">${c.label} ${dateTagHtml}</div>${valueHtml}${changesHtml}</div>`;
    }).join('');
}

function updateSingleChart(materialKey, data, unit, freq) {
    if (!singleChartInstance) return;
    if (data.length === 0) {
        singleChartInstance.clear();
        singleChartInstance.setOption({
            title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#9aa6b5' } }
        });
        return;
    }

    const rate = unit === 'CNY' ? 1 : 0.14;
    const unitLabel = unit === 'CNY' ? '元/吨' : '美元/吨';
    const dates = data.map(d => d.date);
    const prices = data.map(d => Math.round(d.price * rate));

    const option = {
        tooltip: {
            trigger: 'axis',
            backgroundColor: '#fff',
            borderColor: '#e9edf4',
            borderWidth: 1,
            textStyle: { color: '#1e293b' },
            formatter: function(params) {
                const p = params[0];
                return `<strong>${p.axisValue}</strong><br/>价格：<strong>${p.value.toLocaleString()}</strong> ${unitLabel}`;
            }
        },
        grid: {
            left: '5%',
            right: '5%',
            bottom: '10%',
            top: '6%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: dates,
            axisLine: { lineStyle: { color: '#dce2ec' } },
            axisLabel: { color: '#6b7a8f', fontSize: 11 },
            splitLine: { show: false },
            axisTick: { show: false }
        },
        yAxis: {
            type: 'value',
            splitLine: { lineStyle: { color: '#f0f4fa', type: 'dashed' } },
            axisLabel: { color: '#6b7a8f', fontSize: 11 },
            name: unitLabel,
            nameTextStyle: { color: '#9aa6b5', fontSize: 12 }
        },
        series: [{
            data: prices,
            type: 'line',
            smooth: true,
            symbol: 'circle',
            symbolSize: 4,
            lineStyle: { color: '#2b6c9e', width: 2.5 },
            itemStyle: { color: '#2b6c9e' },
            areaStyle: {
                color: {
                    type: 'linear',
                    x: 0, y: 0, x2: 0, y2: 1,
                    colorStops: [
                        { offset: 0, color: 'rgba(43, 108, 158, 0.15)' },
                        { offset: 1, color: 'rgba(43, 108, 158, 0.02)' }
                    ]
                }
            }
        }]
    };

    singleChartInstance.setOption(option, true);
}

let multiChartInstance = null;

function initMultiPage() {
    multiChartInstance = echarts.init(document.getElementById('multiChart'));
}

function downloadChartImage(chartId) {
    alert('下载图片功能开发中...');
}

function downloadChartData(chartId) {
    if (chartId === 'singleChart') {
        const csv = ['日期,价格'].concat(singleCurrentData.map(d => `${d.date},${d.price}`)).join('\n');
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = '价格数据.csv';
        link.click();
    }
}

document.querySelectorAll('.nav-item[data-page]').forEach(item => {
    item.addEventListener('click', function() {
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
        
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        const pageId = 'page-' + this.dataset.page;
        document.getElementById(pageId).classList.add('active');
        
        document.getElementById('pageTitle').textContent = this.textContent.trim();
    });
});

initStreamlit();
