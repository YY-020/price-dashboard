# 市场日报系统 · 项目规则

## 架构快照（动态更新）

### 文件职责清单
| 文件 | 职责 | 只做一件事？ |
|:---|:---|:---|
| crawler/base.py | 所有渠道共用的工具方法（网络请求、去重） | ✅ |
| crawler/rss.py | RSS 渠道通用解析器（只做 XML 解析） | ✅ |
| crawler/html.py | HTML 正文提取器（封装 newspaper4k） | ✅ |
| crawler/scheduler.py | 调度器：读配置 → 匹配渠道 → 调用渠道爬虫 | ✅ |
| crawler/channels/electrive.py | Electrive 渠道爬虫（RSS 采集） | ✅ |
| crawler/channels/ofweek.py | 维科网渠道爬虫（列表页翻页 + 详情页提取） | ✅ |
| crawler/channels/battery_news_de.py | Battery-News-DE 渠道爬虫（RSS 采集） | ✅ |
| crawler/channels/marklines.py | MarkLines 渠道爬虫（列表页解析 + 详情页提取） | ✅ |
| crawler/channels/thelec.py | Thelec 渠道爬虫（列表页解析 + 详情页提取） | ✅ |
| crawler/utils/date_utils.py | 日期解析工具（parse_rss_date、extract_date_from_url） | ✅ |
| crawler/utils/filters.py | URL/标题过滤工具 | ✅ |
| crawler/utils/text_utils.py | HTML 清洗工具 | ✅ |
| utils/llm_client.py | DeepSeek API 统一客户端 | ✅ |
| utils/output_namer.py | 输出文件命名器 | ✅ |
| news_organizer.py | 调用大模型理解新闻内容，输出标准化标签 | ✅ |
| news_filter.py | 基于标签做规则筛选 | ✅ |
| news_summarizer.py | 为中文新闻生成高质量摘要 | ✅ |
| news_translator.py | 英文 → 中文翻译（不含摘要生成） | ✅ |
| report_generator.py | 生成日报文本 | ✅ |
| channel_evaluation.py | 渠道评估（相关性、独特性、效率、时效性、稳定性） | ✅ |
| run.py | 唯一入口，解析命令行参数，启动 pipeline | ✅ |
| main_pipeline.py | 流程编排（采集→整理→筛选→摘要→翻译→日报→评估） | ✅ |

### 渠道特定逻辑清单
| 渠道 | 特有逻辑 | 实现位置 |
|:---|:---|:---|
| 维科网 | 列表页翻页规则、日期从 URL/DOM 提取、gbk 编码、摘要提取策略 | crawler/channels/ofweek.py |
| Electrive | RSS URL 配置、pubDate 解析 | crawler/channels/electrive.py |
| Battery-News-DE | RSS URL 配置、英文日期解析 | crawler/channels/battery_news_de.py |
| MarkLines | 列表页 DOM 解析、日期格式识别 | crawler/channels/marklines.py |
| Thelec | 列表页 DOM 解析、韩文/中文日期格式 | crawler/channels/thelec.py |

## 一、项目目标

每日自动生成一份锂电/电解液行业新闻日报草稿，供市场分析师审核后发送给团队。

## 二、核心需求

### 2.1 新闻采集
- 有固定的信息采集渠道（具体渠道清单见 CONTEXT.md）
- 采集过去 24 小时（昨天 00:00 到今天 08:00）发布的新闻

### 2.2 新闻筛选
- 按照 CONTEXT.md 中定义的筛选规则自动筛选
- 符合筛选标准的新闻全部保留，不限制数量
- 不符合标准的新闻标注删除原因，输出删除报告

### 2.3 新闻整理
- 按 CONTEXT.md 中定义的分类标准归类
- 每条新闻标注：话题标签、企业标签、优先级
- 每条新闻写一句简洁摘要

### 2.4 日报生成
- 按简洁模板生成日报草稿
- 输出格式待讨论：纯文本/邮件/HTML链接/可视化
- 日报需要人工审核后才能发送

## 输出文件命名规范
- 正式产出文件：固定文件名（如 raw_news.xlsx、daily_report.txt），每次覆盖
- 测试产出文件：自动包含日期和渠道标识（如 raw_news_0625_electrive.xlsx）
- 历史文件：归档到 02_Output/archive/ 下，不要留在根目录
- 禁止使用 run_demo3.py、test.py 这种无意义命名

命名规则实现：
- 当指定 `--channels` 参数时，自动添加 `_日期_渠道名` 后缀
- 当指定 `--start` 和 `--end` 参数时（非默认日期），自动添加日期后缀

### 2.5 推送
- 推送方式待讨论：微信、邮箱为主，钉钉/Teams 可考虑
- 审核通过后再推送，不直接发送

## 三、约束条件

- 新闻来源固定，不自行添加或删除渠道
- 筛选规则以 CONTEXT.md 为准
- 日报模板保持简洁，不添加多余模块
- 数据安全：日报仅供内部使用，不对外公开发布
- 全流程自动化：除最终人工审核环节外，采集→筛选→整理→生成→推送全部自动完成，不预设“做不到”的假设

## 四、当前状态

✅ 架构重构完成：职责清晰，渠道特定逻辑与通用逻辑分离
✅ 输出文件动态命名：已实现日期+渠道后缀
✅ 翻译与摘要分离：translator 只做翻译，summarizer 负责摘要生成
✅ 维科网采集能力恢复：列表页翻页、日期提取、摘要提取
✅ Demo 版可用：Electrive 3 版块的全流程已跑通
✅ API Key 集中管理：统一到 constants.py
✅ 新增3个渠道：Battery-News-DE、MarkLines、Thelec
✅ 渠道评估模块：相关性、独特性、效率、时效性、稳定性

### 架构
```
run.py（唯一入口）
  └── main_pipeline.py（流程编排）
        ├── crawler/scheduler.py → crawler/channels/ → raw_news.xlsx     （采集）
        ├── news_organizer.py   → organized_news.xlsx                    （分类标签）
        ├── news_filter.py      → filtered_news.xlsx                     （规则筛选）
        ├── news_summarizer.py  → filtered_news.xlsx                     （摘要生成）
        ├── news_translator.py  → filtered_news.xlsx                     （翻译）
        ├── report_generator.py → daily_report.txt                       （日报生成）
        └── channel_evaluation.py → daily_report_eval.txt                （渠道评估）
```

### 核心字段体系
- **产业链**：政策/EV/ESS/新兴应用/锂电池/固态电池/电解液/CNT/矿/电池回收/其他
- **动态类型**：政策法规/趋势数据/重大技术/产能变动/订单/收并购/新产品发布/其他
- **重要性**：高/中/低（高/中→保留，低→排除）

## 五、交付要求

- 先给出理解和方案，等用户确认后再执行

## 六、参考文件

- 项目宪法：`../TOP_PROJECT.md`
- 业务大背景：`../TOP_CONTEXT.md`
- 日报业务规则：`CONTEXT.md`
- 参考文件：`_DOCS/` 中的周报SOP和4月新闻样例