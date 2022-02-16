wait 1

set systemTime [clock seconds]

broadcast "The time is: [clock format $systemTime -format %H:%M:%S]"

wait 5

#newfile HISTOGRAM_XY
#
#save 0
#wait 20

wait 5

wait 3