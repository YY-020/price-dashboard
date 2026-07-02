content = open(r'd:\0_trea_projects_by_bela\price_dashboard\01_Build\static\ui_prototype.html', 'r', encoding='utf-8').read()
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'freqLabel' in line:
        print(f'Line {i+1}: {repr(line.strip())}')