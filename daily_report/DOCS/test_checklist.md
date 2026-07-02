测试项	怎么测	预期结果
Electrive RSS采集	python run.py --channels electrive_battery --start 2026-06-08 --end 2026-06-12	能抓到10+条新闻，标题和摘要正确
维科网HTML采集	python run.py --channels weike_lidian --start 2026-06-08 --end 2026-06-12	能抓到30+条新闻，摘要不共用
完整链路	python run.py --start 2026-06-08 --end 2026-06-12 --channels electrive_battery,weike_lidian	日报输出正常，保留数量接近人工版
参数传递	python run.py（无参数）	默认采集昨天到今天的所有渠道
这个清单可以放在 daily_report/_DOCS/test_checklist.md 里，不需要写代码。