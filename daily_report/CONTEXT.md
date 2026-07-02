# 日报系统 · 业务规则

## 一、新闻采集渠道

### 固定网站（6个）

| 渠道名称 | URL |
|:---|:---|
| Electrive-Battery | https://www.electrive.com/category/battery-fuel-cell/ |
| Electrive-Auto | https://www.electrive.com/category/automobile/ |
| Electrive-Politics | https://www.electrive.com/category/politics/ |
| MarkLines-CN-News | https://www.marklines.com/cn/news/tag/181/ev-battery |
| Battery-News-DE | https://battery-news.de/en/home/ |
| Thelec | https://www.thelec.net/news/articleList.html?sc_section_code=S1N4&view_type=sm |

### 官网类（12个）

| 渠道名称 | URL |
|:---|:---|
| PowerCo | https://www.powerco.de/en/news.html |
| CATL | https://www.catl.com/news/ |
| SK On | http://eng.sk-on.com/company/press.asp |
| Samsung SDI | https://www.samsungsdi.com/sdi-now/sdi-news/list.html |
| Panasonic | https://news.panasonic.com/global/articles/search/category/all/recent?category=all&type=press |
| 天赐材料 | https://www.tinci.com/zxzx/ |
| BYD | https://www.byd.com/en/news-list |
| 新宙邦 Capchem | https://www.capchem.com/news/2/ |
| 瑞泰新材 RTXC | http://www.rtxc.com/?list_19/ |
| 三菱化学 CGC | https://www.mcgc.com/english/news_release/index.html |
| DS Electera | https://www.dselectera.com/cn/board/board.php?bo_table=press |

### 微信公众号

| 公众号名称 |
|:---|
| 高工锂电 |
| 起点锂电 |
| 我的电池网 |
| 动力电池网 |
| 鑫椤锂电 |
| 维科网锂电 |

### 备注
- 以上为当前固定渠道。过往新闻中存在少量其他网站来源（约10%），作为后续渠道扩展优化项，当前版本暂不纳入。

### 采集频率
- 每次采集过去24小时发布的新闻
- 当前阶段：手动触发（用户主动要求生成日报时运行）
- 后续阶段：每天自动采集（待流程稳定后配置定时任务）

---

## 二、新闻筛选规则（业务宪法）

### 四大层级（产业链自上而下）

| 层级 | 关注点 | 说明 |
|:---|:---|:---|
| Layer 1：宏观环境层 | 政策、关税、地缘政治 | 改变行业成本结构或准入门槛的"游戏规则"变动 |
| Layer 2：需求与应用层 | 新能源车、储能、新兴应用 | 决定电池和材料的出货方向 |
| Layer 3：核心制造层 | 电池厂动态 | 产业链"链主"，链主吃什么材料跟着喝汤 |
| Layer 4：材料与供应链层 | 电解液、CNT、矿端 | 自身主场，关注颗粒度极细的产能和技术变动 |

### 话题标签

政策 / 新能源车 / 储能 / 锂电池 / 固态电池 / 电解液 / CNT / 矿产 / 新兴应用 / 电池回收

### 五条价值判断标准

符合以下任一标准的新闻应当保留：

1. **量级感与确定性**：涉及具体金额（如百亿级投资）、具体产能（如 GWh/TWh 级别）、具体时间节点
2. **卡脖子技术与专利战**：核心专利纠纷、巨额诉讼、技术突破——往往预示行业洗牌
3. **区域性破冰或封死**：出海建厂、海外上市、封杀令、关税裁决——直接关系出海战略
4. **技术代差或路线确立**：固态电池量产时间表、快充技术突破——影响材料需求和技术方向
5. **重大地缘政治/政策事件**：中美/中欧会晤、关税投票、出口管制、地缘冲突（比如美伊战争）——强制收录，置顶显示

### 噪音过滤

以下新闻应当排除：
- 纯股价/财报数据（除非涉及重大亏损或退市）
- 模糊的"将考虑""探索""计划"等没有实质落地动作的新闻
- 纯广告/软文，无实质信息
- 传统汽车新闻（与新能源/电动化无关）
- 非核心高管人事变动

---

## 三、新闻分类标准

| 话题标签 | 关键词/判断依据 |
|:---|:---|
| **政策** | 关税、贸易壁垒、补贴、IRA、关键原材料法案、电池护照、碳足迹、反补贴、出口管制、领导人会晤、贸易谈判 |
| **新能源车** | 电动车、EV、电动汽车、乘用车、商用车、新能源车、销量、产能、电池布局 |
| **储能** | 储能、ESS、BESS、电站、电网、调频、数据中心储能 |
| **锂电池** | 电池、锂电、电芯、GWh、TWh、产线、4680、4695、大圆柱、钠离子电池 |
| **固态电池** | 固态、固液混合、固态电解质、硫化物、氧化物 |
| **电解液** | 电解液、六氟磷酸锂、LiFSI、溶剂、DMC、EMC、EC、DEC、添加剂、VC、FEC |
| **CNT** | 碳纳米管、CNT、导电剂、单壁、多壁、导电浆料 |
| **矿产** | 锂矿、碳酸锂、氢氧化锂 |
| **新兴应用** | eVTOL、飞行汽车、电动船舶、机器人、人形机器人、AI数据中心 |
| **电池回收** | 退役电池、梯次利用、电池回收、second-life、电池拆解、黑粉、再生材料 |

### 核心字段体系（organized 模块输出）

三个标准化字段，大模型只能从固定选项中选择：

| 字段 | 标准选项 |
|:---|:---|
| **产业链** | 政策 / EV / ESS / 新兴应用 / 锂电池 / 固态电池 / 电解液 / CNT / 矿 / 电池回收 / 其他 |
| **动态类型** | 政策法规 / 趋势数据 / 重大技术 / 产能变动 / 订单 / 收并购 / 新产品发布 / 其他 |
| **重要性** | 高 / 中 / 低（高/中→保留，低→排除） |

### 筛选规则（filter 模块）

- 重要性=高 → 保留，⭐高
- 重要性=中 → 保留，●中
- 重要性=低 → 排除
- 地区=其他 + 产业链≠矿 → 排除（兜底规则）

---

## 四、企业白名单（32家）

### 电池企业（16家）

宁德时代 CATL、比亚迪 BYD、LGES、SK On、SDI、远景 Envision AESC、国轩高科 Gotion、PowerCo、松下 Panasonic、特斯拉 Tesla、亿纬 EVE、CALB（中创新航）、瑞普兰钧 REPT、海辰储能 Hithium、欣旺达 Sunwoda

### 电解液企业（16家）

天赐 Tinci、新宙邦Capchem、威海财金、中央硝子 CGC、东和化成 DongWha、德山 Duksan、Elyte、亿恩科 Enchem、国泰华荣/瑞泰新材 RTXC、Soulbrain、珠海赛纬 Smoothway、石大胜华 Shinghwa、昆仑化学Kunlun、永太科技 Yonta、中华蓝天 SINOCHEM LANTIAN

---

## 五、日报输出格式

### 当前约定
- Demo版：纯文本格式，手动转发到微信
- 正式版：HTML邮件格式，自动发送

### 简洁模板
📅 锂电行业日报 | YYYY年MM月DD日

🚨 重大事件
（如有重大地缘政治/政策事件，置顶显示）

⭐ 重点关注
（所有符合筛选标准的高价值新闻，按话题分类排列）
每条格式：[话题标签] 新闻标题 + 一句话摘要

📌 数据速览
（如有价格数据或销量数据）

### 输出格式演进路径
- Demo版 → 纯文本（微信转发）
- 正式版 → HTML邮件（自动发送）
- 进阶版 → 海报式（月度汇报/领导层展示）

---

## 六、新闻整理要求

### 处理流程
```
raw_news → organized（分类标签） → filter（规则筛选） → translate（翻译） → report（日报）
```

### 翻译策略
- 使用 news_translator.py 独立模块，放在 filter 之后执行
- 只翻译筛选结果=保留的新闻，排除和待审核的新闻不翻译
- 翻译后的中文标题和摘要存储在 filtered_news.xlsx 的标题_CN 和摘要_CN 字段
- API 失败时自动回退到英文原文，不中断流程

### 每条新闻由 organized 模块标注
- **产业链**：从标准选项中选择（政策/EV/ESS/新兴应用/锂电池/固态电池/电解液/CNT/矿/电池回收/其他）
- **动态类型**：从标准选项中选择（政策法规/趋势数据/重大技术/产能变动/订单/收并购/新产品发布/其他）
- **重要性**：高/中/低
- **地区**：中国/欧洲/美国/全球/其他
- **涉及企业**：从白名单中识别的标准化企业名称

---

## 七、参考文件

- 周报SOP：`_DOCS/` 中的原始业务规范
- 4月新闻样例：`_DOCS/` 中的历史新闻Excel，可参考实际筛选效果