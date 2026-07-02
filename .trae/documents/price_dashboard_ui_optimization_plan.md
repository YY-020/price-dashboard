# 价格看板 UI 优化计划

## 一、问题分析

### 1. 语言按钮设计问题
- **现状**: 使用国旗 emoji + 文字（🇨🇳 中文 / 🇺🇸 English）的组合，视觉上不够专业
- **影响**: 破坏整体设计风格的一致性，显得突兀

### 2. 英文翻译不完整
- **现状**: 切换到英文后，KPI卡片标签、图表标题、材料分类名称、图例等仍为中文
- **影响**: 国际用户无法正常使用，专业度不足

### 3. 数据标签问题
- **现状**: DIY数据标签使用prompt输入，样式简陋，无法删除已添加的标签
- **影响**: 用户体验差，无法有效管理自定义标注

### 4. 最高/最低值标签无图例
- **现状**: ECharts自动生成的max/min标记没有图例说明
- **影响**: 用户无法理解红色/绿色标记的含义

### 5. 单材料标题缺失单位信息
- **现状**: 图表标题只显示材料名称和时间范围，缺少单位
- **影响**: 用户需要额外查看筛选条件才能知道价格单位

### 6. 价格曲线样式问题（新增）
- **现状**: 曲线有折角，数据点默认显示圆点，不够简洁
- **影响**: 视觉不够流畅，数据点过多导致图表杂乱

### 7. KPI卡片样式问题（新增）
- **现状**: 数值和标签对比度不足
- **影响**: 关键数据不够突出

### 8. 侧边栏图标问题（新增）
- **现状**: 使用emoji图标不够专业
- **影响**: 整体专业度不足

---

## 二、优化方案

### 模块1: 语言切换按钮重构

**修改文件**: `price_dashboard/01_Build/static/ui_prototype.html`

**优化内容**:
- 将国旗emoji替换为简洁的语言标识（CN/EN）
- 使用更现代的按钮设计（圆角 + 渐变边框）
- 添加语言切换动画效果

---

### 模块2: 完整英文翻译

**修改文件**: `price_dashboard/01_Build/static/ui_prototype.html`

**优化内容**:
- 添加材料分类名称的英文翻译（上游-原材料 → Upstream-Raw Materials）
- 添加KPI卡片标签的英文翻译（最新价格 → Latest Price）
- 添加图表标题的英文翻译
- 添加图例单位的英文翻译（RMB/t → USD/t）
- 添加汇率备注的英文翻译

---

### 模块3: DIY数据标签优化

**修改文件**: `price_dashboard/01_Build/static/ui_prototype.html`

**优化内容**:
- 将prompt输入改为点击数据点时弹出浮动输入框
- 标签样式：带引线的小圆点 + 半透明背景的标签框
- 标签删除：鼠标悬浮标签时显示✕按钮，点击可删除
- 使用localStorage保存用户自定义标签

---

### 模块4: 最高/最低值标签图例

**修改文件**: `price_dashboard/01_Build/static/ui_prototype.html`

**优化内容**:
- 在图表头部区域添加自定义图例，说明最高值（红色）和最低值（绿色）标记
- 图例位置：图表左上角，与图表标题并排

---

### 模块5: 单材料标题添加单位

**修改文件**: `price_dashboard/01_Build/static/ui_prototype.html`

**优化内容**:
- 在单材料图表标题中添加单位信息
- 格式："碳酸锂 (Li₂CO₃) 日度价格走势 2025-07-01 至 2026-07-01（单位：万元/吨）"

---

### 模块6: 价格曲线样式优化（新增）

**修改文件**: `price_dashboard/01_Build/static/ui_prototype.html`

**优化内容**:
- 所有折线改为平滑曲线（smooth: true）
- 默认不显示数据点（showSymbol: false）
- DIY标签数据点：蓝色小圆点
- 最高值点：红色圆点
- 最低值点：绿色圆点
- 其他数据点不显示标记

---

### 模块7: KPI卡片样式优化（新增）

**修改文件**: `price_dashboard/01_Build/static/ui_prototype.html`

**优化内容**:
- 数值：大号深色字体（28px, #0b2b4a）
- 标签：浅灰色小字（12px, #9aa6b5）
- 涨跌幅：红色/绿色高亮显示

---

### 模块8: 侧边栏图标优化（新增）

**修改文件**: `price_dashboard/01_Build/static/ui_prototype.html`

**优化内容**:
- 将emoji替换为内联SVG图标
- 使用简洁的线性图标风格
- 图标与文字对齐

---

## 三、文件修改清单

| 文件路径 | 修改内容 | 优先级 |
|---------|---------|--------|
| `01_Build/static/ui_prototype.html` | 语言按钮样式重构 | 高 |
| `01_Build/static/ui_prototype.html` | 完整英文翻译 | 高 |
| `01_Build/static/ui_prototype.html` | DIY数据标签优化 | 高 |
| `01_Build/static/ui_prototype.html` | 最高/最低值图例 | 中 |
| `01_Build/static/ui_prototype.html` | 单材料标题添加单位 | 高 |
| `01_Build/static/ui_prototype.html` | 价格曲线样式优化 | 高 |
| `01_Build/static/ui_prototype.html` | KPI卡片样式优化 | 中 |
| `01_Build/static/ui_prototype.html` | 侧边栏SVG图标 | 中 |

---

## 四、技术实现要点

### ECharts曲线样式
- 使用 `smooth: true` 实现平滑曲线
- 设置 `showSymbol: false` 隐藏默认数据点
- 使用 `markPoint` 独立渲染最高值、最低值和DIY标签
- markPoint配置：
  - 最高值：symbol为circle，itemStyle为红色
  - 最低值：symbol为circle，itemStyle为绿色
  - DIY标签：symbol为circle，itemStyle为蓝色

### DIY标签删除功能
- 使用ECharts的click事件监听
- 鼠标悬浮时显示✕按钮（通过tooltip formatter注入HTML）
- 点击✕按钮触发标签删除逻辑

### SVG图标
- 使用内联SVG，避免引入外部图标库
- 图标尺寸统一为18x18px
- 使用currentColor继承父元素颜色

---

## 五、测试计划

1. **语言切换测试**: 切换中英文，检查所有UI元素是否正确翻译
2. **数据标签测试**: 添加、删除标签，刷新页面验证持久化
3. **图表功能测试**: 验证曲线平滑、数据点显示规则、图例显示
4. **KPI卡片测试**: 验证样式对比度和涨跌幅颜色
5. **响应式测试**: 不同屏幕尺寸下的布局适应性
6. **数据准确性测试**: 验证单位显示与实际数据一致