
set NUM_LOOP 1000000

histmem mode time
histmem preset 30

for {set i 0} {$i < $NUM_LOOP} {incr i} {
	
	broadcast loop $i
	broadcast histmem start
	histmem start block
	
	wait 2
	
	broadcast histmem stop
	histmem stop
	wait 3

	broadcast "The time is: [clock format [clock seconds] -format {%H:%M:%S}]"
	
}