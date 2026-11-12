"""Rebuild pokedex_viewer/index.html from viewer.html without reprocessing the videos.
Usage: python3 rebuild_viewer.py [output_folder] [region_name_for_old_single_video_data]"""
import json, os, sys
out = sys.argv[1] if len(sys.argv) > 1 else 'pokedex_viewer'
name = sys.argv[2] if len(sys.argv) > 2 else 'Kanto'
here = os.path.dirname(os.path.abspath(__file__))
data = None
if os.path.exists(f'{out}/data.json'):
    data = json.load(open(f'{out}/data.json'))
elif os.path.exists(f'{out}/index.html'):
    for line in open(f'{out}/index.html', encoding='utf-8'):   # recover the data saved inside the page
        line = line.strip()
        for key in ('const R = ', 'const D = '):
            if line.startswith(key) and line.endswith(';') and '/*DATA*/' not in line:
                data = json.loads(line[len(key):-1])
if data is None: sys.exit(f'No Pokémon data found in {out}. Run process_pokedex.py again (it now also saves {out}/data.json).')
if isinstance(data, dict):   # old single-video format -> one region, spacing stored on each page
    data = [{'name': name, 'pages': [{**p, 'pad': data['pad'], 'gap': data['gap']} for p in data['pages']]}]
json.dump(data, open(f'{out}/data.json', 'w'))
page = open(os.path.join(here, 'viewer.html'), encoding='utf-8').read()
if '/*DATA*/[]' not in page: sys.exit('viewer.html is not the template file. Download it again and put it next to this script.')
open(f'{out}/index.html', 'w', encoding='utf-8').write(page.replace('/*DATA*/[]', json.dumps(data)))
print(f'Rebuilt {out}/index.html with {sum(len(r["pages"]) for r in data)} Pokémon in {len(data)} region(s)')
