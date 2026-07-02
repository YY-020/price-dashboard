content = open(r'd:\0_trea_projects_by_bela\price_dashboard\01_Build\static\dashboard.html', 'r', encoding='utf-8').read()

# Check for const freqLabel
const_count = content.count('const freqLabel')
let_count = content.count('let freqLabel')

print(f'const freqLabel count: {const_count}')
print(f'let freqLabel count: {let_count}')

# Check for multiDateApply
multi_date_apply_count = content.count('multiDateApply')
print(f'multiDateApply count: {multi_date_apply_count}')

# Check if multiDateApply button exists in HTML
if 'id="multiDateApply"' in content:
    print('multiDateApply button exists in HTML')
else:
    print('multiDateApply button does NOT exist in HTML')

# Check if updateLanguage references multiDateApply
if 'multiDateApply' in content and 'getElementById' in content:
    print('updateLanguage references multiDateApply')