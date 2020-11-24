import plantbox
import os, sys
import serial
import serial.tools.list_ports
from threading import *
from tkinter import *
from tkinter.font import Font
from tkinter import messagebox
from tkinter.ttk import *
from tkinter.messagebox import *
from time import *

class Application_ui(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Plant Box')
        self.master.geometry('1000x500')
        self.createWidgets()
 
    def createWidgets(self):
        self.top = self.winfo_toplevel() 
        self.style = Style()

        self.notebook = Notebook(self.top)
        self.notebook.place(relx=0.05, rely=0.05, relwidth=0.887, relheight=0.876)
 
class Application(Application_ui):
    def __init__(self, master=None):
        Application_ui.__init__(self, master)

    def newTab(self):
        self.count = 0
        self.TabStrip1__Tab1 = Frame(self.notebook)
        #s = plantBoxTab(self.notebook)
        #self.notebook.add(s, text='Plant Box '+ str(self.count))
        #self.addbutton = Button(self.notebook, width = 2, text = '+', command = self.addTab)
        
        #print(self.notebook.tabs)      
        
        self.addTab()
        emptyFrame = Frame()
        self.notebook.add(emptyFrame, text='+')
        print()
        self.notebook.bind("<<NotebookTabChanged>>", self.addTabButton)
        
    def addTabButton(self,ev):
        if self.notebook.select() == '.!frame':
            self.addTab()        

    def addTab(self):
        s = plantBoxTab(self.notebook)
        self.notebook.add(s, text='Plant Box '+ str(self.count))
        self.notebook.insert(self.count,s)
        self.notebook.select(self.count)
        self.count +=1

class plantBoxTab(Frame):
    lables = ['参数名', '当前读数','预设定值', '调节状态']
    port_list = list(serial.tools.list_ports.comports())    
    def __init__(self, master = None):
        self._lock = Lock()
        Frame.__init__(self, master)
        self._pb = plantbox.plantbox()
        self._entryPopup = None

        tnhLabel = Label(self,text= '温湿度传感器')
        tnhLabel.place(relx=0.1,rely=0.025)
        self.cmbTnh = Combobox(self)
        self.cmbTnh.grid_size()
        self.cmbTnh.place(relx=0.2,rely=0.025)
        self.cmbTnh['value'] = plantBoxTab.port_list

        distanceLabel = Label(self,text='液位传感器')
        distanceLabel.place(relx=0.5,rely=0.025)
        self.cmbDistance = Combobox(self)
        self.cmbDistance.grid_size()
        self.cmbDistance.place(relx=0.6,rely=0.025)
        self.cmbDistance['value'] = plantBoxTab.port_list

        self.settings = Treeview(self,column = plantBoxTab.lables,show='headings')        
        self.cmbTnh.bind("<<ComboboxSelected>>",self.tnhEventHandler)       
        self.cmbDistance.bind("<<ComboboxSelected>>",self.distanceEventHandler)

        self.settings.bind('<Double-1>',self.editMode)
        p = Thread(target=self.threadUpd)
        p.setDaemon(True)
        p.start()
        
        self.settings.place(relx=0,rely=0.1)
        for i in plantBoxTab.lables:
            self.settings.heading(i, text = i)

    def editMode(self, event):
        if self._entryPopup:
            self._entryPopup.destroy()
        column = self.settings.identify_column(event.x)
        row = self.settings.identify_row(event.y)
        #不是第三格调参则退出
        if column != '#3':
            return
        print(column)
        
        print(self.settings.index(row))
        print(self.settings.parent(row))
        x,y,width,height = self.settings.bbox(row,column)
        print(self.settings.bbox(row,column))
        
        distance = str(self.settings.item(row, 'values')[2])
        self._entryPopup = SettingEntry(self.settings, text= distance, width=12)       
        self._entryPopup.bind('<Return>', self.handlerAdaptor(self.setting, item = row))
        self._entryPopup.place( x=x, y=y)
        
    
    def handlerAdaptor(self, fun,**kwds):
        return lambda event,fun=fun,kwds=kwds:fun(event,**kwds)

    def setting(self, event, item):
        textInput = self._entryPopup.get()
        if textInput.isdigit:
            textInput = int(textInput)
            self.settings.set(item, column=2, value= textInput)
            self._entryPopup.destroy()
            if item == '温度':
                self._pb.settingTemp(temperture = textInput)
            #if item == '湿度':
                #+++++self._pb.settingTemp(temperture = textInput)
        else:
            messagebox.showerror('Error','请输入正确数字')
        

    def distanceEventHandler(self, event):
        portNumber = plantBoxTab.port_list[self.cmbDistance.current()].device
        try:
            self._pb.openDistancePort(portNumber)
            messagebox.showinfo('Success','打开成功')
        except serial.serialutil.SerialException:
            messagebox.showerror('Error','打开失败') 
        print(serial.tools.list_ports.comports())
        plantBoxTab.port_list = list(serial.tools.list_ports.comports())

    def tnhEventHandler(self, event):            
        portNumber = plantBoxTab.port_list[self.cmbTnh.current()].device
        
        try:
            self._pb.openTnhPort(portNumber)
            messagebox.showinfo('Success','Open Success')
        except serial.serialutil.SerialException:
            messagebox.showerror('Error','Open Fail')

        plantBoxTab.port_list = list(serial.tools.list_ports.comports())

    def threadUpd(self):
        while True:
            sleep(1)
            if self._pb.tnhIsOpen:
                try:
                    self.settings.set(item='温度',column=1, value=str(self._pb.temperture))
                    self.settings.set(item='温度',column=3, value=self._pb.status)
                    self.settings.set(item='湿度',column=1, value=str(self._pb.humidity))
                    self.settings.set(item='湿度',column=3, value=self._pb.status)
                except:
                    self.settings.insert('','end',iid='温度',values=['温度', '0.0','None',plantbox.Status.QUERYING.value])
                    self.settings.insert('','end',iid='湿度', values=['湿度', '0.0','None',plantbox.Status.QUERYING.value])
            if self._pb.distanceIsOpen:
                try:
                    self.settings.set(item='液位',column=1, value=str(self._pb.distance))
                    self.settings.set(item='液位',column=3, value=self._pb.distanceStatus)
                except:
                    self.settings.insert('','end',iid='液位',values=['液位', '0.0','None',plantbox.Status.QUERYING.value])
                
class SettingEntry(Entry):
    '''
    Pop up entry
    '''
    def __init__(self, parent, text:str, **kw):
        Entry.__init__(*(self, parent), **kw)
        if text.isdigit():
            self.insert(0, text)
        '''
        self['readonlybackground'] = 'white'
        self['selectbackground'] = '#1BA1E2'
        self['exportselection'] = False
        '''
        self.focus_force()
        self.bind("<Control-a>", self.selectAll)
        self.bind("<Escape>", lambda *ignore: self.destroy())
 
    def selectAll(self, *ignore):
        self.selection_range(0, 'end')
        return 'break'           

if __name__ == "__main__":
    top = Tk()
    t = Application(top)
    t.newTab()
    t.mainloop()
    