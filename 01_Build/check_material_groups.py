content = open(r'd:\0_trea_projects_by_bela\price_dashboard\01_Build\static\dashboard.html', 'r', encoding='utf-8').read()

# Find the DASHBOARD_DATA script
start = content.find('window.DASHBOARD_DATA =')
if start != -1:
    end = content.find('</script>', start)
    data_script = content[start:end]
    print('Found DASHBOARD_DATA script')
    
    # Check if material_groups is included
    if 'material_groups' in data_script:
        print('material_groups is included')
    else:
        print('material_groups is NOT included')
        
    # Check if materials is included
    if 'materials' in data_script:
        print('materials is included')
    else:
        print('materials is NOT included')
        
    # Count lines
    lines = data_script.split('\n')
    print(f'DATA script lines: {len(lines)}')
else:
    print('DASHBOARD_DATA script not found')