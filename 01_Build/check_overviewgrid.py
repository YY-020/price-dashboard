content = open(r'd:\0_trea_projects_by_bela\price_dashboard\01_Build\static\dashboard.html', 'r', encoding='utf-8').read()

# Find overviewGrid
idx = content.find('overviewGrid')
print(f'overviewGrid found at position: {idx}')

# Check context
start = max(0, idx - 100)
end = min(len(content), idx + 100)
print(f'Context: {repr(content[start:end])}')

# Count occurrences
count = content.count('overviewGrid')
print(f'overviewGrid count: {count}')

# Check overviewPage
idx2 = content.find('overviewPage')
print(f'overviewPage found at position: {idx2}')

# Check context
start2 = max(0, idx2 - 100)
end2 = min(len(content), idx2 + 100)
print(f'Context: {repr(content[start2:end2])}')