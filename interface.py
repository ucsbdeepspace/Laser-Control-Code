from Tkinter import *
import serial
import time

def doNothing():
    """
    As the name may suggest, this function does nothing. Returns immediately.
    We use it as a default function for buttons, so that by default buttons do nothing.
    """
    return
    
class Toggle():
    """
    The Toggle is a wrapper class for a tkinter button that allows it to store an on/off
    state and to call two different functions depending on if it is turned on or off.
    This should probably extend Button itself, but as of right now it's a wrapper.
    """
    
    def __init__(self, frame,xpos,ypos, onText, offText,onFunc=doNothing, offFunc=doNothing):
        """
        Create a new Toggle, starting in the off position.
         - frame: the tkinter frame object to mount this in. This can either be the
                  application's frame or a subframe inside of it.
         - xpos: The GRID x-position of the button. We use grid positioning, so this is
                 in grid position, not pixels.
         - ypos: y-position on grid.
         - onText: The string to be displayed while the Toggle is in the on state
                   (clicked an odd # of times)
         - offText: The string to be displayed while the Toggle is in the off state.
         - onFunc: A function that will be called (with no arguments) every time the
                   Toggle is turned on (default do nothing).
         - offFunc: A function that will be called (with no arguments) every time the
                    Toggle is turned off (default do nothing).
        """
        self.onText = onText
        self.offText = offText
        self.onFunc = onFunc
        self.offFunc = offFunc
        self.state = False
        self.button = Button(
            frame, text=offText, fg="black", command=self.switch # set up the button to call switch() when called so we can call appropriate function.
            )
        self.button.grid(row=ypos, column=xpos)



    def switch(self):
        """
        Called when the Toggle is clicked: Turns Toggle off if on and vice versa.
        Also changes the color of the text and the text to reflect off/on position.
        """
        self.state = not self.state # toggle
        if(self.state): # update text and color
            self.onFunc()
            self.button.configure(fg="red")
            self.button.configure(text=self.onText) 
        else:
            self.offFunc()
            self.button.configure(fg="black")
            self.button.configure(text=self.offText)
        

class App(Frame):

    """
    The actual GUI. Handles setup of the frame and control of the serial communications.
    """

    def __init__(self, master, serlist):
        """
        sets up the button and does boring interface stuff.
        master - tkinter root usually
        serlist - a list of every laser serial port
        """
        Frame.__init__(self, master)
        frame = Frame(master)
        self.root = master
        self.serlist = serlist
        print self.serlist

        self.pack(fill=BOTH, expand=1) #This is just gui setup stuff, not important
        
        self.toggle1 = Toggle(self, 0,0, "Power Off", "Power On ",self.powerOn, self.powerOff) #Each toggle has two different functions, one to turn on and one to turn off.
        self.toggle2 = Toggle(self, 0,1, "Pilot Off", "Pilot On ",self.pilotOn, self.pilotOff)
        self.toggle2 = Toggle(self, 0,2, "Laser Off", "Laser On ",self.laserOn, self.laserOff)
        self.updatePower = Button(self, text='Update power',command=self.updatePower)
        self.updatePower.grid(row=3,column=0) # make toggle buttons to send the commands

        self.selection = []
        buttons = []
        self.pwrlist = []
        for i in range(len(serlist)): # Each laser gets a readout and checkbox added to GUI
            intvar = IntVar()
            self.selection += [intvar]
            serbutton = Checkbutton(self, text="Laser-"+str(i), variable=intvar) 
            serbutton.grid(row=i, column=1)
            buttons += [serbutton]
            pwr = Text(self, height = 2, width = 6)
            pwr.grid(row=i,column=2)
            self.pwrlist += [pwr]

        self.txt = Text(self, height = 10, width = 50)#Create a console for error messages
        self.txt.grid(row=6,column=0,columnspan=5)

        self.power = StringVar()
        self.entry = Entry(self,textvariable=self.power,text='laser power (0-1000)') #Make a text box that can be queried by self.power.get()
        self.entry.grid(row=4,column=0)

    def log(self,where, string):
        """Logs both to the text in the gui and to console. use as print()"""
        self.txt.insert(where, string+'\n')
        print(string)

    #So now we get to the serial commands. You should read all of
    #M:\Manuals-Books\Dilas Mini 50 - 50W 808nm USB Laser\THIS_IS_THE_IMPORTANT_ONE
    #This is named THIS_IS_THE_IMPORTANT_ONE because it is the only pdf with anything important
    #in the entire folder (that's not actually true, but whatever)

    #Please read page 53-61 for more info, but I'll describe below what's important about this.
    #This info should also be available in "dilas_command_info.txt"

    def sendCommand(self, command, logName):
        """
        Send a serial command to all selected lasers and log a message to console.
         - command: the command to be sent, ie "Stp1"
         - logName: name of command to be logged, ie "powerOn"
        """
        self.log(INSERT, logName+": "+command)
        for i in range(len(self.serlist)):
            if(self.selection[i].get()):
                self.serlist[i].write(command+'\r')

    def powerOn(self): # think of power like a safety: laser can't shoot without it, but turning it on doesn't fire the laser.
        sendCommand('Stp1', 'powerOn')
        
    def powerOff(self):
        sendCommand('Stp0', 'powerOff')

    def pilotOn(self): # little red laser for aiming the invisible death laser
        sendCommand('Sto1', 'pilotOn')

    def pilotOff(self):
        sendCommand('Sto0', 'pilotOff')

    def laserOn(self): # turn on invisible death laser
        sendCommand('Stl1', 'laserOn')

    def laserOff(self):
        sendCommand('Stl0', 'laserOff')
        
    def updatePower(self): # range fro 0-1000 set the power of the invisible death laser
        sendCommand('Sti'+self.power.get(), 'updatePower')

    def pingPowdisp(self): #send a query to the laser asking for power info. 
        for i in range(len(self.serlist)):
            if(self.selection[i].get()):
                ser = self.serlist[i]
                ser.flushOutput()
                ser.flushInput()
                ser.write('Rdo\r')
        self.root.after(50, self.updatePowerdisp)

    def updatePowerdisp(self): # update the text file based on poorly checked power info that more than likely is actually a response from the laser. todo fix this
        for i in range(len(serlist)):
            ser = serlist[i]
            while ser.inWaiting():
                raw = (ser.readline())
                self.pwrlist[i].delete('0.0', 'end')
                self.pwrlist[i].insert(INSERT, raw+'\n')
                
    def checkUpdates(self, count): #Read from all lasers and log them to the console, also update powerdisp.
        for i in range(len(serlist)):
            ser = serlist[i]
            while ser.inWaiting():
                raw = (ser.readline())
                raw = raw.strip()
                if raw:
                    string = 'Laser '+str(i)+ ' > ' + raw
                    self.log(INSERT, string)
        if count %4 == 0:
            self.pingPowdisp()

        self.root.after(100, self.checkUpdates, count+1)

serlist=[]

def addToSerlist(com, timeout = 5, baud = 115200, l = serlist):
    s = serial.Serial(com)
    s.timeout = timeout
    s.setBaudrate(baud)
    l += [s]

def addAllToSerlist(strSerList):
    for s in strSerList:
        addToSerlist(s)


comlist = ['COM8','COM5','COM7','COM10']

print ("The current list of lasers is:")
print ("Ensure all of these lasers are plugged in and powered on.")

#Lasers must be plugged in and powered on (not so laser is emitting but so the fan is running)
#in order for this serial connection to work. In order to find which serial port a laser is on,
#open Device Manager, navigate to the "ports" tab, and open it. Then unplug the laser you want
#to identify, and find which port dissapears when you unplug it. Confirm that you have the
#correct one by checking that it reappaears when you plug it back in.

#If the program throws a connection error, try restarting the lasers, unplugging and plugging again 

print comlist
choice = raw_input("Is this correct? N to import custom list (Y/n)")
if (choice[0].lower()) == "n":
    #create new comlist
    comlist = []
    comname = raw_input("Enter COM port exactly in this format: \"COM1\" or type anything else to finish comlist: ")
    while comname[0:3] == "COM":
        comlist += comname
        comname = raw_input("Enter COM port exactly in this format: \"COM1\" or type anything else to finish comlist: ")

print "usinc comlist " + str(comlist)

try:
    addAllToSerlist(comlist)
except Exception as ex:
    print ex
    print 'error in creating COM ports! Shutting down. \nCheck lasers are plugged in and powered on!'
    for ser in serlist:
        ser.close()

for i in range(len(serlist)):
    ser = serlist[i]
    ser.write("Wrv0\r") #disable st100 terminal emulation, no matter how cool it looks.
    while ser.inWaiting():
        raw = (ser.readline())
        raw = raw.strip()
        if raw:
            string = 'Laser '+str(i)+ ' > ' + raw
            self.log(INSERT, string)

try: # setup GUI and run mainloop 
    root = Tk()
    root.geometry("480x360+300+300")
    print serlist
    app = App(root,serlist)
    root.after(100, app.checkUpdates, 0)
    root.mainloop()
except Exception as ex:
    print ex
    print 'error in tkinter creation! Shutting down.'
    for ser in serlist:
        ser.close()
for ser in serlist:
    ser.close()
