Drive sc -150

Drive sxtop 1.5

Omega_2theta 0.85 1.7 0.73 3.13 2.00

Rel som -0.05

Samplename Si/bilayer/D2O om0.85

Runscan dummy_motor 0 0 1 time 600 force true

 

Omega_2theta 3.5 7.0 3.01 12.89 5.00

Rel som -0.05

Samplename Si/bilayer/D2O om3.5

Runscan dummy_motor 0 0 1 time 3600 force true

 

#The equivalent on Platypus would look something like:

#Angler(0)
#
#Positioner(1)
#
#acquire(600, mode = "time", samplename = " Si/bilayer/D2O om0.85")
#
# 
#
#Angler(1)
#
#Positioner(1)
#
#acquire(3600, mode = "time", samplename = " Si/bilayer/D2O om3.5")