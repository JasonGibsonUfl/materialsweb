import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','materialsweb2.settings')

import django
django.setup()

from simulation import *
from simulation.analysis.vasp.calculation import Calculation    
import os
a=os.walk('/var/www/materialsweb/static/database')
for b in a:
        c=b[0].split('/')
        if c[-1] != 'pbe_bands' and c[-1] != 'hse_bands':
                path = '/var/www/materialsweb/static/database/'+c[-1]
                try:
                    calc = Calculation().read(path)  
                    calc.create_all(path)
                    calc.save()
                except:
                    print(path+'')


