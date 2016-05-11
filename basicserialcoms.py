import serial
import time

s = serial.Serial('COM5')
s.timeout = 5
s.setBaudrate(115200)
serlist = [s]
for ser in serlist:
    ser.write("Wrv0\r") #disable st100 terminal emulation, no matter how cool it looks.
selection = [0]*len(serlist)
try:
    while True:
        for i in range(len(serlist)):
            ser = serlist[i]
            if ser.inWaiting():
                print 'Laser',i, '>', (ser.read(ser.inWaiting())).strip()
        string = raw_input("> ")+'\r'
        if 'Sel' in string: #adding my own commands to handle selecting which lasers to use
            selection[int(string[3])] = True #Sel[x] adds a laser to the list.
        elif 'Dsl' in string:
            selection[int(string[3])] = False #Dsl[x] removes a laser from list
        elif 'Rsl' in string: #Rsl prints the selection list
            print selection
        else:
            for i in range(len(selection)):
                if selection[i]:
                    serlist[i].write(string)
        time.sleep(0.05)
except KeyboardInterrupt:
    for ser in serlist:
        ser.close()
    print 'Keyboard interrupt! Shutting down!'
    raise KeyboardInterrupt
except Exception as err:
    for ser in serlist:
        ser.close()
    raise err
