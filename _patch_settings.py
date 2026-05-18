import pathlib
p = pathlib.Path('placement_portal/settings.py')
t = p.read_text()
old = "    'dashboard',\n    'rest_framework',"
new = "    'dashboard',\n    'analytics',\n    'rest_framework',"
t = t.replace(old, new)
p.write_text(t)
print('Done:', 'analytics' in t)
