# 市场日报系统

## 简介
每日自动生成一份锂电/电解液行业新闻日报草稿，供市场分析师审核后发送给团队。

## 文件夹结构
| 文件夹 | 用途 |
|:---|:---|
| `00_Inbox/` | 存放采集到的原始新闻 |
| `01_Build/` | 代码文件 |
| `02_Output/` | 生成的日报文件 |
| `_DOCS/` | 参考文档（周报SOP、历史新闻样例） |

## 核心规则
- 新闻来源：18个固定网站 + 6个微信公众号（详见 CONTEXT.md）
- 筛选标准：基于业务宪法四层金字塔 + 五条价值判断（详见 CONTEXT.md）
- 全流程自动化，仅最终审核需要人工介入
- 日报格式和推送方式待确定

## 当前状态
✅ Demo 可用：Electrive 3 版块全流程已跑通。
⏳ 翻译：已接入 DeepSeek API，待充值验证。
⏳ 全渠道：待接入 MarkLines / Battery-News-DE / Thelec 等渠道。

## 架构
```
main_pipeline.py --demo --start YYYY-MM-DD --end YYYY-MM-DD
  ├── Step 1: news_crawler.py    → 02_Output/raw_news.xlsx
  ├── Step 2: news_filter.py     → 02_Output/filtered_news.xlsx
  ├── Step 3: news_organizer.py  → 02_Output/organized_news.xlsx
  └── Step 4: report_generator.py → 02_Output/daily_report.txt
```

## 关联文件
- 项目规则：`PROJECT.md`
- 业务规则：`CONTEXT.md`
- 项目宪法：`../TOP_PROJECT.md`