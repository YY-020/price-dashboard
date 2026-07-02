content = open(r'd:\0_trea_projects_by_bela\price_dashboard\01_Build\static\dashboard.html', 'r', encoding='utf-8').read()
lines = content.split('\n')
count = 0
for i, line in enumerate(lines):
    if 'freqLabel' in line:
        count += 1
        print(f'Line {i+1}: {line.strip()}')
print(f'Total: {count}')