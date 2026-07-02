import glob

files = glob.glob(r'd:\0_trea_projects_by_bela\price_dashboard\**\*.html', recursive=True)
for file in files:
    try:
        content = open(file, 'r', encoding='utf-8').read()
        if 'freqLabel' in content and 'const freqLabel' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'const freqLabel' in line:
                    print(f'{file}:{i+1}: {line.strip()}')
    except:
        pass