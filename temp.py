import os
a=os.walk('.')
from pathlib import Path
from shutil import copyfile

for b in a:

    c = (b[0].split('/'))
    if '.git' in c or '__pycache__' in c or '.ipynb_checkpoints' in c or '.idea' in c:
        pass
    else:
        path = Path(b[0]+'/__init__.py')
        if path.is_file() == False:
           copyfile('./__init__.py',b[0]+'/__init__.py')