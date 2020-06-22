#!/usr/bin/env python

import sys
if not 'matplotlib' in sys.modules:
    import matplotlib
    try:
        matplotlib.use('WXAgg')
    except:
        matplotlib.use('Agg')

class RenderingError(Exception):
    pass


class Renderable(object):
    def draw_in_matplotlib(self, **kwargs):
        raise NotImplementedError

    def get_flot_series(self, **kwargs):
        raise NotImplementedError

    def get_matplotlib_script(self, **kwargs):
        raise NotImplementedError

