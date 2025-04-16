#------------------------------------------------------------------------------
# Description: This file contains the commands to run the BNN training.
#              Note: the data-spec format assumes that all inputs in the
#                    training file are used and the last column is the
#                    target.
# Created: Sat Nov 26 03:39:26 2016 by mktrain.py
#------------------------------------------------------------------------------
#	1	ht
#	2	met
#	3	njets
#------------------------------------------------------------------------------
echo "File: MetMhtSextetReal"

net-spec	MetMhtSextetReal.bin 3 10 1 / - 0.05:0.5 0.05:0.5 - x0.05:0.5 - 100

model-spec	MetMhtSextetReal.bin binary

data-spec	MetMhtSextetReal.bin 3 1 2 / MetMhtSextetReal.dat@2:85448 . MetMhtSextetReal.dat@2:85448 .

net-gen		MetMhtSextetReal.bin fix 0.5

mc-spec		MetMhtSextetReal.bin repeat 20 heatbath hybrid 100:10 0.2

net-mc		MetMhtSextetReal.bin 1

mc-spec MetMhtSextetReal.bin repeat 20 sample-sigmas heatbath 0.95 hybrid 100:10 0.2

echo "Start chain"
echo "Use"
echo "   net-display -h MetMhtSextetReal.bin"
echo "periodically to check the progress of the chain"

time net-mc	MetMhtSextetReal.bin 250

echo ""
echo "Use"
echo "   netwrite.py -n 100 MetMhtSextetReal.bin"
echo "to create the BNN function MetMhtSextetReal.cpp using the last 100 points"
