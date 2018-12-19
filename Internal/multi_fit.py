from gumpy.nexus.fitting import Fitting, GAUSSIAN_FITTING
from gumpy.vis.event import MouseListener
import traceback, sys
# Script control setup area
# script info
__script__.title = 'Muiti-Peak fitting'
__script__.version = '0.1'

DS = None
SELECTED_PEAK = 1
NUM_PEAK = 4
CURRENT_FOCUS = None

class NavMouseListener(MouseListener):
    
    def __init__(self):
        MouseListener.__init__(self)
        
    def on_click(self, event):
        x = event.getX()
#        y = event.getY()
        pick_value(x)
#        updatePlot2(y)
#        updatePlot3(x)

# Use below example to create parameters.
# The type can be string, int, float, bool, file.
for i in range(1, NUM_PEAK + 1):
    p1 = '''peak$I_select = Par("bool", False, command="toggle_peak($I)")
peak$I_select.title = "Select peak $I"
peak$I_min = Par("float", "NaN")
peak$I_min.enabled = False 
peak$I_min.title = "min X"
peak$I_min.focus = "set_focus('peak$I_min')"
peak$I_max = Par("float", "NaN")
peak$I_max.enabled = False
peak$I_max.title = "max X"
peak$I_max.focus = "set_focus('peak$I_max')"
peak$I_act = Act("fit_curve($I)", "Fit peak $I")
peak$I_act.enabled = False
peak$I_mean = Par("flaot", "NaN")
peak$I_mean.enabled = False
peak$I_mean.title = "peak $I value"
peak$I_FWHM = Par("float", "NaN")
peak$I_FWHM.enabled = False
peak$I_FWHM.title = "FWHM"
g$I = Group("Peak $I")
g$I.add(peak$I_select, peak$I_min, peak$I_max, peak$I_act, peak$I_mean, peak$I_FWHM)
'''
    exec(p1.replace('$I', str(i)))

def toggle_peak(p):
    global SELECTED_PEAK
    SELECTED_PEAK = p
    for i in range(1, NUM_PEAK + 1) :
        if i == p:
            print 'enable', i
            exec('peak{}_select.value=True'.format(i))
            exec('peak{}_min.enabled=True'.format(i))
            exec('peak{}_max.enabled=True'.format(i))
            exec('peak{}_act.enabled=True'.format(i))
            exec('peak{}_mean.enabled=True'.format(i))
            exec('peak{}_FWHM.enabled=True'.format(i))
            exec('g{}.highlight=True'.format(i))
        else:
            print 'disable', i
            exec('peak{}_select.value={}'.format(i, 'False'))
            exec('peak{}_min.enabled={}'.format(i, 'False'))
            exec('peak{}_max.enabled={}'.format(i, 'False'))
            exec('peak{}_act.enabled={}'.format(i, 'False'))
            exec('peak{}_mean.enabled={}'.format(i, 'False'))
            exec('peak{}_FWHM.enabled={}'.format(i, 'False'))
            exec('g{}.highlight=False'.format(i))
    set_focus('peak{}_min'.format(p))
    
def set_focus(input):
    global CURRENT_FOCUS
    if input != None:
        ie = eval('{}.enabled'.format(input))
        if ie == 'True' :
            if CURRENT_FOCUS != None:
                exec('{}.highlight=False'.format(CURRENT_FOCUS))
            exec('{}.highlight=True'.format(input))
            CURRENT_FOCUS = input
        else :
            if CURRENT_FOCUS != None:
                exec('{}.highlight=False'.format(CURRENT_FOCUS))
            CURRENT_FOCUS = None
    else:
        if CURRENT_FOCUS != None:
            exec('{}.highlight=False'.format(CURRENT_FOCUS))
        CURRENT_FOCUS = None
        
def pick_value(val):
    global CURRENT_FOCUS
    if CURRENT_FOCUS != None:
        exec('{}.value={}'.format(CURRENT_FOCUS, val))
        if CURRENT_FOCUS.endswith('min'):
            nf = CURRENT_FOCUS.replace('min', 'max')
            set_focus(nf)
        elif CURRENT_FOCUS.endswith('max'):
            set_focus(None)
    
def fit_curve(i):
    global Plot2
    ds = Plot2.ds
    if len(ds) == 0:
        log('Error: no curve to fit in Plot2.\n')
        return
    for d in ds:
        if d.title == 'fitting':
            Plot2.remove_dataset(d)
    d0 = ds[0]
    fitting = Fitting(GAUSSIAN_FITTING)
    try:
        min = eval('peak{}_min.value'.format(i))
        max = eval('peak{}_max.value'.format(i))
        fitting.set_histogram(d0, min, max)
        val = eval('peak{}_mean.value'.format(i))
        if val == val:
            fitting.set_param('mean', val)
        val = eval('peak{}_FWHM.value'.format(i))
        if val == val:
            fitting.set_param('sigma', math.fabs(val / 2.35482))
        res = fitting.fit()
        res.var[:] = 0
        res.title = 'fitting'
        Plot2.add_dataset(res)
        Plot2.pv.getPlot().setCurveMarkerVisible(Plot2.__get_NXseries__(res), False)
        mean = fitting.params['mean']
        mean_err = fitting.errors['mean']
        FWHM = 2.35482 * math.fabs(fitting.params['sigma'])
        exec('peak{}_FWHM.value={}'.format(i, FWHM))
        FWHM_err = 5.54518 * math.fabs(fitting.errors['sigma'])
        log('POS_OF_PEAK_{}={} +/- {}'.format(i, mean, mean_err))
        log('FWHM=' + str(FWHM) + ' +/- ' + str(FWHM_err))
#        log('Chi2 = ' + str(fitting.fitter.getQuality()))
        exec('peak{}_mean.value = {}'.format(i, fitting.mean))
#        print fitting.params
    except:
        traceback.print_exc(file = sys.stdout)
        log('can not fit\n')


# Use below example to create a new Plot
# Plot4 = Plot(title = 'new plot')

# This function is called when pushing the Run button in the control UI.
def __run_script__(fns):
    # Use the provided resources, please don't remove.
    global Plot1
    global Plot2
    global Plot3
    
    # check if a list of file names has been given
    if (fns is None or len(fns) == 0) :
        print 'no input datasets'
    else :
        if len(fns) > 0:
            # load dataset with each file name
            ds = df[fns[0]]
            if ds.ndim == 4:
                sl = ds[0, 0]
            else:
                sl = ds[0]
            a1 = sl.axes[1]
            if a1.size > 1 and a1[0] > a1[-1]:
                ns = simpledata.zeros(sl.shape)
                xl = sl.shape[1]
                for i in xrange(xl):
                    ns[:, i] = sl[:, xl - 1 - i]
                ns.title = sl.title
                xl = a1.size
                na = simpledata.zeros([xl])
                for i in xrange(xl):
                    na[i] = a1[xl - 1 - i]
                na.title = a1.title
                na.units = a1.units
                nv = ns.float_copy()
                sl = Dataset(ns, var = nv, axes = [sl.axes[0], na])
            Plot1.set_dataset(sl)
            Plot1.set_mouse_listener(NavMouseListener())
            Plot1.title = ds.title
            it = sl.intg(0)
            it.title = 'integration'
            Plot2.set_dataset(it)
            Plot2.title = ds.title
            Plot2.y_label = 'Y Integration'
            Plot2.x_label = a1.title
            Plot2.set_mouse_listener(NavMouseListener())
            Plot2.select_dataset(it)
    
def __dispose__():
    global Plot1
    global Plot2
    global Plot3
    Plot1.clear()
    Plot2.clear()
    Plot3.clear()
