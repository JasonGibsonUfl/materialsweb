import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','materialsweb2.settings')

import django
django.setup()

from simulation import *
from simulation.analysis.vasp.calculation import Calculation    
import os
a=os.walk('/var/www/materialsweb/static/database/MAX_phases/')
for b in a:
        if len(b[1])==0:
           path = b[0]
           try:
               print(path)
               calc = Calculation().read(path)
               calc.create_all(path)
               calc.save()
           except:
               print(path)
'''
for b in a:
        c=b[0].split('/')
        if c[-1] != 'pbe_bands' and c[-1] != 'hse_bands':
                path = '/var/www/materialsweb/static/database/MAX_phases/all_competitors/'+c[-1]
                try:
                    calc = Calculation().read(path)
                    calc.create_all(path)
                    calc.save()
                    #print('Path: '+path)
                except:
                    print(path+'')
'''


