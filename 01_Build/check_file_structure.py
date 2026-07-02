content = open(r'd:\0_trea_projects_by_bela\price_dashboard\01_Build\static\dashboard.html', 'r', encoding='utf-8').read()

# Check basic structure
print(f'File size: {len(content)} bytes')
print(f'<html> count: {content.count("<html")}')
print(f'</html> count: {content.count("</html")}')
print(f'<body> count: {content.count("<body")}')
print(f'</body> count: {content.count("</body")}')
print(f'<script> count: {content.count("<script")}')
print(f'</script> count: {content.count("</script")}')

# Check if body ends properly
body_end_idx = content.rfind('</body>')
html_end_idx = content.rfind('</html>')
print(f'</body> at: {body_end_idx}')
print(f'</html> at: {html_end_idx}')

# Check last 500 characters
print(f'\nLast 500 chars:')
print(repr(content[-500:]))