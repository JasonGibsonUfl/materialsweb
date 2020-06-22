import simulation
from simulation import *
from simulation.analysis.vasp.calculation import Calculation    
import os
a=os.walk('/var/www/materialsweb/static/database')
def run():
    for b in a:
        c=b[0].split('/')
        if c[-1] != 'pbe_bands' and c[-1] != 'hse_bands':
            from simulation.analysis.vasp.calculation import Calculation

            path = ('var/www/materialsweb/static/database/'+c[-1])
            calc = simulation.analysis.vasp.calculation.Calcualtion().read(path)
            #calc = calc.read(path)
            calc.create_all(path)
            calc.save()
