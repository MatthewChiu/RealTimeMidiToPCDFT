# # import time and rtmidi package

# import rtmidi

# # the function call rtmidi.Midiout() creates the handler that we'll use to send midi signals
# midiout = rtmidi.MidiOut()

# # check and get the ports which are open
# available_ports = midiout.get_ports()


#%%
import sys
import rtmidi
import time
import numpy as np


midiin = rtmidi.RtMidiIn()


# ——————————————————————————————————————————————————
def print_message(midi):
    if midi.isNoteOn():
        print('ON: ', midi.getMidiNoteName(midi.getNoteNumber()), midi.getVelocity())
    elif midi.isNoteOff():
        print('OFF:', midi.getMidiNoteName(midi.getNoteNumber()))
    elif midi.isController():
        print('CONTROLLER', midi.getControllerNumber(), midi.getControllerValue())


def windower(listOfPitchesAndTimes, windowSizeMemory):
    timeLength = listOfPitchesAndTimes[-1][1] - listOfPitchesAndTimes[0][1]
    windowedArray = [[] for x in range(0, timeLength+1)]
    startingPosition = listOfPitchesAndTimes[0][1]

    previousPosition = 0
    for thing in listOfPitchesAndTimes:
        for index in range(0, windowSizeMemory):
            if (thing[1]-startingPosition+index) <= timeLength:
                windowedArray[(thing[1]-startingPosition)+index].append(thing[0]%12)

    return windowedArray

# —————————————————————————————————
# DFT/Characteristic Functions
# Takes the storage information and weights it by Log2 (weighting taken from Matt Chiu).

def characteristicFunction(listOfPCs):
    PCStorage = []
    for counter, window in enumerate(listOfPCs):
        collection = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        PCStorage.append(collection)
        for PC in window:
            PCStorage[counter][PC] += 1
    return PCStorage

def log_weight(stored_pcdata):
    for counter, array in enumerate(stored_pcdata):
        for counter2, element in enumerate(array):
#           Uncomment this for log-weighted input
#             array[counter2] = math.log(element+1, 2)
            
#           Uncomment this for non-log-weighted input
            array[counter2] = element
    return stored_pcdata

# Takes the weighted information, performs the DFT, then grabs the magnitude and phase of each array. Returns a tuple containing lists of lists (magnitues and phases).
def make_arrays(weighted_data):
    DFTArray = []
    magnitudeArray = []
    phaseArray = []
    for x in weighted_data:
        DFTArray.append(np.fft.fft(x)) 
    for eachArray in DFTArray:
        magnitudeArrayGrabber = np.absolute(eachArray)
        normalizedMagnitudes = [x/magnitudeArrayGrabber[0] for x in magnitudeArrayGrabber]
        magnitudeArray.append(normalizedMagnitudes[0:7]) 
        phaseArrayGrabber = np.angle(eachArray)
        phaseArray.append(phaseArrayGrabber)
    return (magnitudeArray, phaseArray, DFTArray)


def logDFT(listOfPCs):
    a = characteristicFunction(listOfPCs)
    x = log_weight(a)
    y = make_arrays(x)
    return y[0]

def averageDFTs(scoreToDataResults):
    averageDFT = []
    for i in range(0,len(scoreToDataResults[0][0])):
        averageDFT.append([0])
    
    windowCount = 0
    for counter, window in enumerate(scoreToDataResults[0]):
        windowCount += 1
        for counter2, element in enumerate(window):
            averageDFT[counter2]+=element
    
    normalizer = averageDFT[0]
    for counter, value in enumerate(averageDFT):
        averageDFT[counter] = float(value/normalizer)

    return averageDFT
# —————————————————————————————————————————————————
# Demonstration
testy = [[66, 1669689390], [67, 1669689397], [67, 1669689397], [67, 1669689397], [68, 1669689398], [68, 1669689398], [68, 1669689398], [68, 1669689398], [69, 1669689399], [70, 1669689400], [70, 1669689400], [70, 1669689400], [71, 1669689401], [71, 1669689401], [71, 1669689401], [71, 1669689401], [71, 1669689401], [72, 1669689402], [72, 1669689402], [72, 1669689402], [72, 1669689402], [73, 1669689403], [73, 1669689403]]
blahBlah = windower(testy, 5)
print(blahBlah)

thing = logDFT(blahBlah)
print(thing[8])


# ———————————————————
# Practice plotting

#%%
import matplotlib.pyplot as plt
fig = plt.figure()

ax = fig.add_subplot(111)

plt.xlabel("Time")
plt.ylabel("Magnitude")

line1, = ax.plot(thing[8])
fig.canvas.draw()

fig.canvas.flush_events()


# —————————————————————————————————————————————————

# %%

# fig = plt.figure()
# ax = fig.add_subplot(111)

import matplotlib as mpl
mpl.rcParams['path.simplify'] = True
mpl.rcParams['path.simplify_threshold'] = 3.0

# Real time code
PCArray = []
ports = range(midiin.getPortCount())
if ports:
    for i in ports:
        print(midiin.getPortName(i))
    print("Opening port 1!") 
    midiin.openPort(1)

    # startingTime = time.localtime(time.time()).tm_sec
    startingTime = int(str(time.time()).split(".")[0])

    while True:
        
        m = midiin.getMessage(250) # some timeout in ms

        # t = time.localtime(time.time())
        t = int(str(time.time()).split(".")[0])

        if "NOTE ON" in str(m):

            # tempPitch = [m.getMidiNoteName(m.getNoteNumber()), t.tm_sec]
            tempPitch = [m.getNoteNumber(), t]

            # print(m)
            # print(tempPitch)
            PCArray.append(tempPitch)

            # print(PCArray)

        if len(PCArray) > 0:
            windowedImprov = windower(PCArray, 5)
            DFTLive = logDFT(windowedImprov)

            plt.cla()
            plt.plot(DFTLive[-1])
            plt.show()


else:
    print('NO MIDI INPUT PORTS!')



# DFTLive then has the data from the performance...





