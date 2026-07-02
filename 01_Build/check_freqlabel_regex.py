import re

content = open(r'd:\0_trea_projects_by_bela\price_dashboard\01_Build\static\dashboard.html', 'r', encoding='utf-8').read()

# Check for exact const freqLabel (not freqLabels)
const_matches = re.findall(r'\bconst freqLabel\b', content)
let_matches = re.findall(r'\blet freqLabel\b', content)
var_matches = re.findall(r'\bvar freqLabel\b', content)

print(f'const freqLabel (exact) count: {len(const_matches)}')
print(f'let freqLabel (exact) count: {len(let_matches)}')
print(f'var freqLabel (exact) count: {len(var_matches)}')

# Find all occurrences with context
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'freqLabel' in line and 'freqLabels' not in line:
        print(f'Line {i+1}: {repr(line.strip())}')