from gumpy.control import control
import os
import time
from gumpy.commons import logger
from org.gumtree.gumnix.sics.io import SicsCallbackAdapter
from org.gumtree.gumnix.sics.control import ServerStatus
from org.gumtree.gumnix.sics.batch.ui.util import SicsBatchUIUtils
import traceback
import sys

def runbmonscan(scan_variable, scan_start, scan_increment, NP, mode, preset, channel, comm = None):
    rawscan('bmonscan', scan_variable, scan_start, scan_increment, NP, mode, preset, channel, comm)

def runhmscan(scan_variable, scan_start, scan_increment, NP, mode, preset, channel, comm = None):
    rawscan('hmscan', scan_variable, scan_start, scan_increment, NP, mode, preset, channel, comm)

def runscan(scan_variable, scan_start, scan_stop, numpoints, mode, preset, comm = None, force = False, \
            datatype = 'HISTOGRAM_XYT', savetype = 'save'):
    # Initialisation
    control.clear_interrupt()
    cpath = '/commands/scan/runscan'
    scanController = control.get_controller(cpath)
    
    control.execute('hset ' + cpath + '/scan_variable ' + str(scan_variable))
    control.execute('hset ' + cpath + '/scan_start ' + str(scan_start))
    control.execute('hset ' + cpath + '/scan_stop ' + str(scan_stop))
    control.execute('hset ' + cpath + '/numpoints ' + str(numpoints))
    control.execute('hset ' + cpath + '/mode ' + mode)
    control.execute('hset ' + cpath + '/preset ' + str(preset))
    control.execute('hset ' + cpath + '/datatype ' + datatype)
    control.execute('hset ' + cpath + '/savetype ' + savetype)
    control.execute('hset ' + cpath + '/force ' + str(force))

    # Monitor status
    while(scanController.getState().equals(control.ControllerState.BUSY)):
        # Don't do anything before scan is ready
        time.sleep(0.1)
    
    # Wait 1 sec to make the setting settle
    time.sleep(1)
    
    # Run scan
    print 'Scan starting'
#    scanController.asyncExecute()
#    control.execute('hset ' + cpath + ' start')
#    control.async_command('hset ' + cpath + ' start', True)
    scanController.run()
    
    # Monitor initial status change
    try:
        timeOut = False
        counter = 0;
        print 'Waiting for scan to start'
        while (scanController.getState().equals(control.ControllerState.IDLE)):
            print(str(scanController.getState()))
            time.sleep(0.1)
            counter += 0.1
            if (counter >= 50):
                timeOut = True
                print 'Time out on running scan'
                break
                
        # Enter into normal sequence
        print 'Scan started'
        if (timeOut == False):
            scanpoint = -1;
            scanPointController = control.get_controller(cpath + '/feedback/scanpoint')
            countsController = control.get_controller(cpath + '/feedback/scan_variable_value')
            print '  NP  ' + '\t' + ' Device Position'
            while (scanController.getState().equals(control.ControllerState.BUSY)):
                try:
                    currentPoint = scanPointController.getValue()
                except:
                    time.sleep(0.1)
                    continue
                if ((scanpoint == -1 and  currentPoint == 0) or (scanpoint != -1 and currentPoint != scanpoint)):
                    scanpoint = currentPoint
                    if currentPoint > 0 :
                        try:
                            print '%4d \t %.4f' % (scanpoint, countsController.getValue())
                        except:
                            pass
                        if not comm is None:
                            try:
#                            if (float(scanpoint) / 3) == (int(scanpoint) /3) :
                                comm()
#                                print '\tupdate plot'
                            except:
                                traceback.print_exc(file = sys.stdout)
                time.sleep(0.1)
            if comm != None:
                try:
                    comm()
                except:
                    pass
            try:
                print '%4d \t %.4f' % (scanpoint + 1, countsController.getValue())
            except:
                pass
            logger.log('Scan completed')
        control.handle_interrupt()
    except Exception, e:
        if e.message == 'SICS interrupted!':
            raise e
        else:
            traceback.print_exc(file = sys.stdout)
            raise Exception, 'failed to run the scan'
    except:
        traceback.print_exc(file = sys.stdout)
        raise Exception, 'failed to run the scan'

def rawscan(type, scan_variable, scan_start, scan_increment, NP, mode, preset, channel, comm):
    # Initialisation
    clearInterrupt()
#    scan_variable = 'dummy_motor'
    cpath = '/commands/scan/' + type
    scanController = control.get_controller('/commands/scan/' + type)
    
    control.execute('hset ' + cpath + '/scan_variable ' + str(scan_variable))
    control.execute('hset ' + cpath + '/scan_start ' + str(scan_start))
    control.execute('hset ' + cpath + '/scan_increment ' + str(scan_increment))
    control.execute('hset ' + cpath + '/NP ' + str(NP))
    control.execute('hset ' + cpath + '/mode ' + mode)
    control.execute('hset ' + cpath + '/preset ' + str(preset))
    control.execute('hset ' + cpath + '/channel ' + str(channel))

    # Monitor status
    while(scanController.getState().equals(control.ControllerState.BUSY)):
        # Don't do anything before scan is ready
        time.sleep(0.1)
    
    # Wait 1 sec to make the setting settle
#    time.sleep(1)
    
    # Run scan
    print 'Scan started'
#    scanController.asyncExecute()
    control.execute('hset ' + cpath + ' start')
    
    # Monitor initial status change
    try:
        timeOut = False
        counter = 0;
        while (scanController.getState().equals(control.ControllerState.IDLE)):
            time.sleep(0.1)
            print 'IDLE'
            counter += 0.1
            if (counter >= 3):
                timeOut = True
                print 'Time out on running scan'
                break
                
        # Enter into normal sequence
        if (timeOut == False):
            scanpoint = -1;
            scanPointController = control.get_controller(cpath + '/feedback/scanpoint')
            countsController = control.get_controller(cpath + '/feedback/scan_variable_value')
            print '  NP  ' + '\t' + ' Counts'
            while (scanController.getState().equals(control.ControllerState.BUSY)):
                try:
                    currentPoint = scanPointController.getValue()
                except:
                    time.sleep(0.1)
                    continue
                if ((scanpoint == -1 and  currentPoint == 0) or (scanpoint != -1 and currentPoint != scanpoint)):
                    scanpoint = currentPoint
                    if currentPoint > 0 :
                        try:
                            print '%4d \t %d' % (scanpoint, countsController.getValue())
                        except:
                            pass
                        if comm != None:
                            try:
#                            if (float(scanpoint) / 3) == (int(scanpoint) /3) :
                                comm()
                                print '\tupdate plot'
                            except:
                                traceback.print_exc(file = sys.stdout)
                time.sleep(0.1)
            if comm != None:
                try:
                    comm()
                except:
                    pass
            try:
                print '%4d \t %d' % (scanpoint + 1, countsController.getValue())
            except:
                pass
            logger.log('Scan completed')
        control.handle_interrupt()
    except Exception, e:
        if e.message == 'SICS interrupted!':
            raise e
        else:
            traceback.print_exc(file = sys.stdout)
            raise Exception, 'failed to run the scan'
    except:
        traceback.print_exc(file = sys.stdout)
        raise Exception, 'failed to run the scan'
        
        
#def getStableValue(dev):
#    val = None
#    while (True):
#        controller = control.get_controller(dev)
#        new_val = controller.getValue(True).getFloatData()
#        if new_val == val :
#            return getValue(dev)
#        else:
#            val = new_val
#            time.sleep(1)
        
#__status__ = None
#class __SICS_Callback__(control.SicsCallback):
#    
#    def receiveReply(self, data):
#        global __status__
#        try:
#            rt = data
#            if rt.__contains__('='):
#                __status__ = data.split("=")[1].strip()
#            elif rt.__contains__(':'):
#                __status__ = data.split(":")[1].strip()
#                if __status__.__contains__('}'):
#                    __status__ = __status__[:__status__.index('}')]
#            self.setCallbackCompleted(True)
#        except:
#            traceback.print_exc(file = sys.stdout)
#            self.setCallbackCompleted(True)

#def runCommand(cmd):
#    global __status__
#    __status__ = None
#    call_back = __SICS_Callback__()
#    SicsCore.getDefaultProxy().send(cmd, call_back)
#    acc_time = 0
#    while __status__ is None and acc_time < 2:
#        time.sleep(0.2)
#        acc_time += 0.2
#    if __status__ is None:
#        raise Exception, 'time out in running the command'
#    return __status__

def scan(device, start, stop, NP, mode, preset, force = False, comm = None):
    runscan(device, start, stop, NP, mode, preset, comm, force)
    

