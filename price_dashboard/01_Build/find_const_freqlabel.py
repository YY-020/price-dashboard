content = open(r'd:\0_trea_projects_by_bela\price_dashboard\01_Build\static\dashboard.html', 'r', encoding='utf-8').read()
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'const freqLabel' in line:
        print(f'Line {i+1}: {repr(line.strip())}')