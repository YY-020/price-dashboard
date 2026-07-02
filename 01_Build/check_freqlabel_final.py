content = open(r'd:\0_trea_projects_by_bela\price_dashboard\01_Build\static\dashboard.html', 'r', encoding='utf-8').read()

# Check for const freqLabel
const_count = content.count('const freqLabel')
let_count = content.count('let freqLabel')

print(f'const freqLabel count: {const_count}')
print(f'let freqLabel count: {let_count}')

# Find all lines with freqLabel
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'freqLabel' in line:
        print(f'Line {i+1}: {repr(line.strip())}')