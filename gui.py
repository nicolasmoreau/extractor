import Tkinter as tk
import hdf
import config as cfg
import util as u
import tkFileDialog, tkMessageBox, tkSimpleDialog
import os
import sys
import sampy as s
import ttk as ttk


__author__ = "Nicolas Moreau"
__copyright__ = "Copyright 2012"
__credits__ = ["Nicolas Moreau"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Nicolas Moreau"
__email__ = "nicolas.moreau@obspm.fr"
__status__ = "Development"  


class TkFactory(object):
    @staticmethod
    def buildButton(container, text, command):
        """
            return a Button object
                container : container widget
                text : text on button
                command : callback function
        """
        return tk.Button(container, text=text, width=20, command=command)
        
    @staticmethod    
    def buildListBox(container, selectmode, listvariable = None):
        """
            return a ListBox object
            container : container widget
            selectmode : line selection mode 
        """
        scrollbar = tk.Scrollbar(container)                
        listbox = tk.Listbox(container, selectmode=selectmode, height=10, yscrollcommand=scrollbar.set, listvariable=listvariable)    
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        scrollbar.config(command=listbox.yview)   
        return listbox 
        
    @staticmethod
    def buildEntry(container, text, width=20):
        entryLabel = tk.Label(container)
        entryLabel["text"] = text    
        entry = tk.Entry(container, width=width)  
        return entry
        
    @staticmethod
    def buildAutocompleteEntry(container, text, width=20):
        entryLabel = tk.Label(container)
        entryLabel["text"] = text    
        entry = AutocompleteCombobox(container)
        return entry
        
    @staticmethod
    def buildMainFrame(size):
        appli = tk.Tk()
        appli.geometry(size)
        frame = MainFrame(appli)
        appli.protocol("WM_DELETE_WINDOW", frame.onDelete)
        appli.mainloop()
        
    @staticmethod
    def buildSampWidget():
        appli = tk.Tk()
        frame = SampWidget(appli, "pdr extractor", "samp extractor test")
        appli.protocol("WM_DELETE_WINDOW", frame.onDelete)
        appli.mainloop()
        
        
class RadioDialog(tkSimpleDialog.Dialog):      
    """
        generic dialog box showing list of radio buttons
    """
    def __init__(self, parent, fields, defaultvalue, windowtitle = None, frametitle=None):      
        """
            parent : container 
            fields : list of titles for radio buttons
            defaultvalue : default selected value
            windowtitle : title of window
            frametitle : text in border of display area
        """
        if len(fields)==0:
            raise Exception("list can not be empty")
            
        if defaultvalue not in fields:
            raise Exception("default value in not in the list")
            
        self.radios = fields
        """ list of radio buttons """
        self.default = defaultvalue
        """ default selected value"""
        self.selectedvalue = tk.StringVar(None, defaultvalue)
        """ currently selected value"""
        self.frameTitle = frametitle        
        """ title of the frame border """
        
        tkSimpleDialog.Dialog.__init__(self, parent, windowtitle)   
        
    def setDefault(self, name):
        """
        value selected by default
        """
        self.default = tk.StringVar(None, name)
        
    def addRadioButton(self, name):
        """        
        add a radio button with text = name
        """
        self.radios.append(name)        

    def body(self, master):     
        """
        build widget, does not need to be called
        """
        frame = tk.LabelFrame(master, text=self.frameTitle, pady=10)        
       
        for value in self.radios:    
            button = tk.Radiobutton(frame, text=value, variable=self.selectedvalue, value=value)    
            button.deselect()
            button.pack(side=tk.LEFT)              
            if value == self.default:
                button.select()        
                
        frame.grid(row=1, column=0, rowspan=2)
        return None      # no focus by default         
        

class SampWidget(object):
    """
    widget managing samp connection and sending messages
    """
    def __init__(self, parent, name, description):
        self.root = parent        
        self.name = name
        """ application name """
        self.description = description
        """ aplication description """
        self.sentTableCount = 0
        """ nuimber of table sent """
        self.client = s.SAMPIntegratedClient()
        """ samp client """
        
        self.statusVar = tk.StringVar()
        """ contains connection status, on or off """
        
        self.__connectionDisabled()
        self.frame = tk.Frame(parent)
        
        statusLabel = tk.Label(self.frame, textvariable=self.statusVar)
        statusLabel.pack()

        self.frame.pack()  
        
    def sendTable(self, filepath) :
        """
        send a votable
        filepath : url of the table
        """
        if self.client.isConnected() is False :  
            self.__connectHub()            
            
        if self.client.isConnected():  
            self.sentTableCount += 1
            self.client.notifyAll({"samp.mtype": "table.load.votable",
                                 "samp.params": {"url": "file:"+filepath, "name":self.name+" table "+str(self.sentTableCount)}})    
                                 
    def pack(self, position):
        """
        call pack function on the container frame
        """
        self.frame.pack(side=position)
        
    def __connectionEnabled(self):
        self.statusVar.set('Samp is On')  
        
    def __connectionDisabled(self):
        self.statusVar.set('Samp is Off')  
        self.sentTableCount = 0
        
        
    def __hubNotification(self, private_key, sender_id, mtype, params, extra):
        """ 
        dispatch messages received from samp hub
        """
        if mtype == 'samp.hub.event.shutdown':
            self.__connectionDisabled()
            self.client.disconnect()        

    def __connectHub(self):   
        """
        establish a connection with samp hub
        """
        try:            
            self.client.connect()
            self.client.declareMetadata(metadata = {"samp.name":self.name,
                       "samp.description.text":self.description,
                       "cli1.version":"1"})
            self.client.bindReceiveNotification("samp.hub.event.shutdown", self.__hubNotification)
            self.client.bindReceiveNotification("samp.hub.disconnect", self.__hubNotification)           
            self.client.declareSubscriptions()
            self.__connectionEnabled()
        except s.SAMPHubError as e: 
            tkMessageBox.showerror("Error", e.value)        
            
'''
class AutocompleteEntry(tk.Entry):
    """ 
    src : http://tkinter.unpythonic.net/wiki/AutocompleteEntry
    Subclass of Tkinter.Entry that features autocompletion.

    To enable autocompletion use set_completion_list(list) to define 
    a list of possible strings to hit.
    To cycle through hits use down and up arrow keys.
    """ 
    def set_completion_list(self, completion_list, special_chars=[]):
        self._completion_list = completion_list
        self._hits = []
        self._hit_index = 0 
        self.position = 0 
        self._specials = special_chars
        self.bind('<KeyRelease>', self.handle_keyrelease)    

    def autocomplete(self, delta=0):
        """autocomplete the Entry, delta may be 0/1/-1 to cycle through possible hits"""
        if delta: # need to delete selection otherwise we would fix the current position
            self.delete(self.position, tk.END)
        else: # set position to end so selection starts where textentry ended
            self.position = len(self.get())
        # collect hits
        _hits = []
        for element in self._completion_list:
            if element.startswith(self.get()):
                _hits.append(element)
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0 
            self._hits=_hits
        # only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # now finally perform the auto completion
        if self._hits:
            self.delete(0,tk.END)
            self.insert(0,self._hits[self._hit_index])
            self.select_range(self.position,tk.END)

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        print "event : ",event.keysym, '   ', event.keycode, '  ', event.char
        if event.keysym == "BackSpace":
            self.delete(self.index(tk.INSERT), tk.END) 
            self.position = self.index(tk.END)
        if event.keysym == "Left":
            if self.position < self.index(tk.END): # delete the selection
                    self.delete(self.position, tk.END)
            else:
                    self.position = self.position-1 # delete one character
                    self.delete(self.position, tk.END)
        if event.keysym == "Right":
            self.position = self.index(tk.END) # go to end (no selection)
        if event.keysym == "Down":
            self.autocomplete(1) # cycle to next hit 
        if event.keysym == "Up":
            self.autocomplete(-1) # cycle to previous hit 
        # perform normal autocomplete if event is a single key or an umlaut
        if len(event.keysym) == 1 or event.char in self._specials:
            print "autocomplete"
            self.autocomplete()
'''

class AutocompleteCombobox(ttk.Combobox): 
        def set_completion_list(self, completion_list, special_chars): 
                """Use our completion list as our drop down selection menu, arrows move through menu.""" 
                self._datasets, self._completion_list = self._cleanautocomplete(sorted(completion_list))
                #self._completion_list = sorted(completion_list) # Work with a sorted list                 
                self._hits = [] 
                self._hit_index = 0 
                self._specials = special_chars
                self._currentgroup = ''
                self.position = 0 
                self.bind('<KeyRelease>', self.handle_keyrelease) 
                self['values'] = self._completion_list  # Setup our popup menu 
                
        def _cleanautocomplete(self, completion_list):
            datasets = []
            columns = []
            
            for value in completion_list:
                parts = value.split(cfg.separator)
                datasets.append(parts[0])
                columns.append(parts[1])
            return datasets, columns
                

        def autocomplete(self, delta=0): 
                """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits""" 
                if delta: # need to delete selection otherwise we would fix the current position 
                    self.delete(self.position, tk.END) 
                else: # set position to end so selection starts where textentry ended 
                    self.position = len(ttk.Combobox.get(self)) 
                # collect hits 
                _hits = [] 
                for element in self._completion_list: 
                    #short_elem = element.split(':')[1]
                    if element.startswith(ttk.Combobox.get(self)): # Match case insensitively 
                        #_hits.append(short_elem) 
                        _hits.append(element) 
                # if we have a new hit list, keep this in mind 
                if _hits != self._hits: 
                    self._hit_index = 0 
                    self._hits=_hits 
                # only allow cycling if we are in a known hit list 
                if _hits == self._hits and self._hits: 
                    self._hit_index = (self._hit_index + delta) % len(self._hits) 
                # now finally perform the auto completion 
                if self._hits: 
                    self.delete(0,tk.END) 
                    self.insert(0,self._hits[self._hit_index]) 
                    self.select_range(self.position,tk.END) 

        def handle_keyrelease(self, event): 
                """event handler for the keyrelease event on this widget""" 
                if event.keysym == "BackSpace": 
                        self.delete(self.index(tk.INSERT), tk.END) 
                        self.position = self.index(tk.END) 
                if event.keysym == "Left": 
                        if self.position < self.index(tk.END): # delete the selection 
                                self.delete(self.position, tk.END) 
                        else: 
                                self.position = self.position-1 # delete one character 
                                self.delete(self.position, tk.END) 
                if event.keysym == "Right": 
                        self.position = self.index(tk.END) # go to end (no selection) 
                if len(event.keysym) == 1 or event.keysym in self._specials: 
                    self.autocomplete() 
                # No need for up/down, we'll jump to the popup 
                # list at the position of the autocompletion 
                
        def get(self):
            value = ttk.Combobox.get(self)
            return self._datasets[self['values'].index(value)]+cfg.internalSeparator+ttk.Combobox.get(self)
             #return "test"+super(AutocompleteCombobox, self).get()
           

class MainFrame(object):
    def __init__(self, parent):      
        self.root = parent      
        
        self.frame = tk.Frame(parent)        
        """ base Frame """
        
        self.exporttextbutton = None
        self.exportvotablebutton = None
        self.exportscriptbutton = None
        self.sampbutton = None     
        self.defaultColumn = None   
        """ column automcatically exported with data for plotting """
        
        self.defaultColumnAdded = False
        """ True when the default column has already been appended to the current selection"""
        
        self.frame.master.title(cfg.applicationName)      
        
        self.contentFrame = None   
        """ content Frame (all the Frame minus menubar) """
         
        self.hdfData = None
        """ PdrHDF object containing PDR HDF5 data """
        
        self.datasets = []
        """ list of dataset names (string) """
        
        self.datasetsBox = None
        """ ListBox containing the title of all datasets"""
        
        self.datasetContentBox = None
        """ ListBox containing the title of columns in one dataset"""
        
        self.currentDataset = None
        """ Name of the currently selected Dataset """
        
        self.exportedDataWidget = None
        """ data selected by user to export (list of strings)"""
        
        self.exportedData = []
        """ data selected by user to export (list of strings)"""
        
        self.exportedDataHeader = None
        
        self.menuButton = None
        """ File menu in the menubar """
        
        self.separator = ','
        """ File menu in the menubar """
        
        self.sampWidget = None
        
        self.precision = cfg.floatPrecision
        
        self.columnDescriptionText = None
        
        self.lastColumns = None
        """ previously selected columns, to display descriptions """
        
        self.autocomplete = None
        
        self.__initUI()
        """ initialize GUI """       

        
    def __initUI(self):   
        """ 
            initialize GUI
        """        
        #build menubar
        menuframe = tk.Frame(self.frame, borderwidth="1", relief="raised")
        menuframe.pack(side=tk.TOP, fill=tk.X)  
        self.__makeMenuBar(menuframe)   

        #widget containing other parts of the interface, not made visible in this method
        self.contentFrame = tk.Frame(self.frame, borderwidth="1", relief="raised")
        
        topframe = tk.LabelFrame(self.contentFrame, text="Dataset", pady=10)
        topframe.grid(rowspan = 1, sticky = tk.W+tk.E+tk.N+tk.S)  
        
        self.datasetsBox = ttk.Combobox(topframe, values=self.datasets, state="readonly")
        self.datasetsBox.bind('<<ComboboxSelected>>', self.__refreshDatasetContent)        
        self.datasetsBox.pack(side=tk.LEFT)      
          
        
        self.autocomplete = TkFactory.buildAutocompleteEntry(topframe, "Enter the text : ", 50)
        self.autocomplete.pack(side=tk.LEFT)            
        
        selectionframe = tk.LabelFrame(self.contentFrame, text="Column", pady=10)      
        selectionframe.grid(row=1,rowspan=2,column=0, sticky = tk.W+tk.E+tk.N+tk.S)   

        #add name of columns in the dataset
        self.datasetContentBox = TkFactory.buildListBox(selectionframe, tk.MULTIPLE)
        self.datasetContentBox.bind('<<ListboxSelect>>', self.__showDescription)
        self.datasetContentBox.pack(side=tk.LEFT)              
        
        #buttons to interact with list of columns
        buttonFrame = tk.Frame(selectionframe)
        buttonFrame.pack(side=tk.LEFT)
        clearButton = TkFactory.buildButton(buttonFrame, "clear selection", self.__clearSelection)  
        clearButton.grid(row=0, column=0)
        selectAllButton =  TkFactory.buildButton(buttonFrame, "select all", lambda : self.datasetContentBox.selection_set(0, tk.END))  
        selectAllButton.grid(row=1, column=0)
        confirmButton =  TkFactory.buildButton(buttonFrame, "confirm", lambda :self.__addSelectedData(self.datasetContentBox.curselection()))  
        confirmButton.grid(row=2, column=0)   
        
        self.columnDescriptionText=tk.Text(selectionframe,height=10,width=50,background='white', state=tk.DISABLED)    
                  
        self.columnDescriptionText.pack(side=tk.LEFT)    
        
        columnframe = tk.LabelFrame(self.contentFrame, text="Selection")           
        columnframe.grid(row=3,column=0, sticky = tk.W+tk.E+tk.N+tk.S)        
       
        #list of selected columns
        self.exportedDataWidget = TkFactory.buildListBox(columnframe, tk.MULTIPLE) 
        self.exportedDataWidget.pack(side=tk.LEFT)
        buttonFrame2 = tk.Frame(columnframe)
        buttonFrame2.pack(side=tk.LEFT)
        clearlisttoexportButton =  TkFactory.buildButton(buttonFrame2, "remove all", self.__cleanSelection)          
        clearlisttoexportButton.grid(row=0, column=0)        
        removeButton =  TkFactory.buildButton(buttonFrame2, "remove", self.__removeSelectedData)  
        removeButton.grid(row=1, column=0)       
        
        #export buttons
        bottomframe =  tk.Frame(self.contentFrame, pady=10)
        bottomframe.grid(row=4, column=0, rowspan = 1, sticky = tk.W+tk.E+tk.N+tk.S)     
      
        self.exporttextbutton = TkFactory.buildButton(bottomframe, "Export as Text", self.__exportAsText)
        self.exporttextbutton.pack(side=tk.LEFT)      
        
        self.exportvotablebutton = TkFactory.buildButton(bottomframe, "Export as Votable", self.__exportAsVotable)
        self.exportvotablebutton.pack(side=tk.LEFT)    
        
        self.exportscriptbutton = TkFactory.buildButton(bottomframe, "Save script", self.__saveScript)            
        self.exportscriptbutton.pack(side=tk.LEFT)       
        
        self.sampbutton = TkFactory.buildButton(bottomframe, "Send Table", self.__sendSampTable)             
        self.sampbutton.pack(side=tk.LEFT)        
        
        self.__setButtonsState(False)
        
        
        self.frame.pack(fill=tk.BOTH, expand=True)    
        
    def __clearSelection(self):
        self.datasetContentBox.selection_clear(0, tk.END)
        self.lastColumns = None
        
    def __showDescription(self, event):
        description = ' '
        if self.lastColumns is not None : 
            diff_list = [item for item in event.widget.curselection() if not item in self.lastColumns]
            if len(diff_list) > 0:
                description = self.hdfData.index[self.currentDataset][event.widget.get(int(diff_list[0]))].description
        else : 
            description = self.hdfData.index[self.currentDataset][event.widget.get(event.widget.curselection()[0])].description
        self.columnDescriptionText.config(state=tk.NORMAL)
        self.columnDescriptionText.delete(1.0, tk.END)
        self.columnDescriptionText.insert(tk.END, description)
        self.columnDescriptionText.config(state=tk.DISABLED)
        self.lastColumns = event.widget.curselection()
       
        
    def __setButtonsState(self, status):
        """
            enable or disable all buttons at once
            status = True : enable, status = False : disable
        """
        if status is True and self.exporttextbutton['state'] == tk.DISABLED : 
            self.exporttextbutton.config(state=tk.NORMAL)     
            self.exportvotablebutton.config(state=tk.NORMAL)     
            self.exportscriptbutton.config(state=tk.NORMAL)     
            self.sampbutton.config(state=tk.NORMAL)     
        elif status is False and self.exporttextbutton['state'] == tk.NORMAL:
            self.exporttextbutton.config(state=tk.DISABLED)     
            self.exportvotablebutton.config(state=tk.DISABLED)     
            self.exportscriptbutton.config(state=tk.DISABLED)     
            self.sampbutton.config(state=tk.DISABLED)     

        
    def loadNewFile(self):   
        """  
            update the GUI after a new file has been loaded
        """        
        self.contentFrame.pack(side=tk.TOP, fill=tk.BOTH)  
        self.datasetsBox['values'] = self.datasets
        self.datasetsBox.set(self.datasets[0])
        self.datasetsBox.event_generate('<<ComboboxSelected>>')
        self.defaultColumn = self.hdfData.getDefaultColumns()[0]
        
        keys = []
        for key in self.hdfData.index:
            for otherkey in self.hdfData.index[key]:
                keys.append(key+cfg.separator+otherkey)
        self.autocomplete.set_completion_list(keys, ['parenleft','parenright','KP_Subtract','KP_Add','minus','equal','plus','=','less','greater','comma','slash', 'KP_Divide','colon'])
        self.autocomplete.bind('<Return>', self.__addColumn)
        
       
    def __makeMenuBar(self, menuContainer):
        """
            build the menu bar
        """                
        self.menuButton = tk.Menubutton(menuContainer, text="File")        
        #self.menuButton.grid()
        self.menuButton.menu=tk.Menu(self.menuButton, tearoff=False)
        self.menuButton["menu"]=self.menuButton.menu
        self.menuButton.menu.add_command(label='Open HDF', command=self.__askOpenHdfFile)        
        self.menuButton.menu.add_command(label='Apply script', command=self.__askOpenScriptFile)        
        self.menuButton.pack(side=tk.LEFT)   
        
        configurationMenuButton = tk.Menubutton(menuContainer, text="Text Configuration")        
        configurationMenuButton.menu=tk.Menu(configurationMenuButton, tearoff=False)
        configurationMenuButton["menu"]=configurationMenuButton.menu
        configurationMenuButton.menu.add_command(label='Separator', command=self.__askChangeSeparator)        
        configurationMenuButton.menu.add_command(label='Precision', command=self.__askConfiguration)  
        configurationMenuButton.pack(side=tk.LEFT)   
        
        self.exportMenuButton = tk.Menubutton(menuContainer, text="Export")        
        self.exportMenuButton.menu=tk.Menu(self.exportMenuButton, tearoff=False)
        self.exportMenuButton["menu"]=self.exportMenuButton.menu
        self.exportMenuButton.menu.add_command(label='Default column', command=self.__askDefaultColumn)        
        self.exportMenuButton.pack(side=tk.LEFT)   
        
        self.sampWidget = SampWidget(menuContainer, "pdr extractor", "samp extractor test")
        self.sampWidget.pack(tk.RIGHT)
        
        #disable some buttons at startup
        self.__switchMenuState(False)
        
    def __askConfiguration(self):
        """
        display widget for choice of precision (float or double)
        """
        d = RadioDialog(self.frame, [cfg.floatPrecision, cfg.doublePrecision], self.precision, "Precision configuration", "Choose precision")
        self.precision = d.selectedvalue.get()
        
    def __askDefaultColumn(self):
        """
        display widget for choosing the default exported column
        """
        columns = self.hdfData.getDefaultColumns()
        
        if self.defaultColumn is None :            
            defaultvalue = columns[0]
        else:
            defaultvalue = self.defaultColumn

        d = RadioDialog(self.frame, columns, defaultvalue, "Default column", "Choose a default column")
        self.defaultColumn = d.selectedvalue.get()
        
    def __askOpenHdfFile(self):
        """Returns an opened file in read mode."""
        filename = tkFileDialog.askopenfilename(filetypes=[(cfg.inputFileDescription,"*."+cfg.inputFileExtension)])
        if os.path.isfile(filename):
            self.__parseHdf(filename)
            self.__switchMenuState(True)
            self.__cleanSelection()
        else:
            tkMessageBox.showerror(filename+" is not a file")
            
    def __askOpenScriptFile(self):
        """Returns an opened file in read mode."""
        filename = tkFileDialog.askopenfilename(filetypes=[(cfg.scriptFileDescription,"*."+cfg.scriptFileExtension)])
        if os.path.isfile(filename):
            self.__execScript(filename)
        else:
            tkMessageBox.showerror(filename+" is not a file")
            
    def __askChangeSeparator(self):
        result = tkSimpleDialog.askstring(title='Set column separator', prompt='New separator :', initialvalue=cfg.separator)
        if len(result) > 0:
            cfg.separator = result
        else :
            tkMessageBox.showwarning("Warning", "Separator can not be empty")
            
            
    def __execScript(self, filename):      
        """
        run an export script
        """
        self.exportedData = u.ScriptReader.getColumns(filename)
        self.precision, self.exportedDataHeader = u.ScriptReader.getHeader(filename)
        self.__exportAsText()
        self.__cleanSelection()
            
    def __parseHdf(self, filename):
        """
        read hdf file
        """
        self.hdfData = hdf.PdrHDF(filename)
        self.datasets = sorted(self.hdfData.index.keys())
        self.loadNewFile()
        
    def __refreshDatasetContent(self, value):
        """
            refresh interface when the selected dataset changes
                value : event that triggered the call of the function
        """
        self.lastColumns = None
        #currently selected group
        self.currentDataset = value.widget.get()
        
        #add name of columns in the dataset
        self.datasetContentBox.delete(0, tk.END)
        for key in sorted(self.hdfData.index[self.currentDataset].keys()):
            self.datasetContentBox.insert(tk.END,key)           
    
    
    def __cleanSelection(self):
        """
        remove all selected data
        """
        self.exportedDataWidget.delete(0, tk.END)
        del self.exportedData[:]
        self.__setButtonsState(False)    
        self.defaultColumnAdded = False     
       
    def __addSelectedData(self, values):
        """
            add selected data to the export list and list widget
        """       
        for i in values:
            self.exportedDataWidget.insert(tk.END,self.currentDataset+':'+self.datasetContentBox.get(i))
            self.exportedData.append(self.currentDataset+cfg.internalSeparator+self.datasetContentBox.get(i))
        if len(self.datasetContentBox.curselection()) >0:
            self.__setButtonsState(True)            
        #clean selection once used        
        self.datasetContentBox.selection_clear(0, tk.END)
        
    def __addColumn(self, event):
        value = event.widget.get().split(cfg.internalSeparator)        
        self.exportedDataWidget.insert(tk.END,value[0]+':'+value[1])
        self.exportedData.append(event.widget.get())
        self.__setButtonsState(True)       # to modify, changing value each time is not necesary
        
        
    def __removeSelectedData(self):
        """
            add selected data to the export list and list widget
        """       
        for i in self.exportedDataWidget.curselection():
            self.exportedData.pop(int(i))
            self.exportedDataWidget.delete(int(i))            

        
    def __saveScript(self):
        """
        export selected coumns as script file
        """
        filename = tkFileDialog.asksaveasfilename(filetypes=[(cfg.scriptFileDescription,"*."+cfg.scriptFileExtension)])
        f = open(filename,'w')
        f.write('#precision:'+self.precision+"\n")
        for value in self.exportedData:
            f.write(value+"\n")
        f.close()    
        
    def __hasMeshOnly(self):
        """
            verify if selected data are only MeshCell
        """
        for value in self.exportedData:
            parts = value.split(cfg.internalSeparator)
            meta = self.hdfData.index[parts[0]][parts[1]]
            if meta.group != 'MeshCell':
                return False
        return True
            
    def __exportAsText(self): 
        """
        export selected data into text file
        """
        self.__appendMeshColumns()
        filename = tkFileDialog.asksaveasfilename(filetypes=[(cfg.txtFileDescription,"*."+cfg.txtFileExtension)])
        
        isDouble = True
        if self.precision == cfg.floatPrecision:
            isDouble = False

        hdf.Exporter.exportAsText(self.hdfData, self.exportedDataHeader, self.exportedData, filename, cfg.separator, isDouble)
        
    def __exportAsVotable(self): 
        """
        export selected data into votable file
        """
        self.__appendMeshColumns()
        filename = tkFileDialog.asksaveasfilename(filetypes=[(cfg.votableFileDescription,"*."+cfg.votableFileExtension)])
        
        isDouble = True
        if self.precision == cfg.floatPrecision:
            isDouble = False

        hdf.Exporter.exportAsVotable(self.hdfData, self.exportedDataHeader, self.exportedData, filename, isDouble)
        
    def __appendMeshColumns(self):
        if self.__hasMeshOnly() and not self.defaultColumnAdded :
            self.exportedData.append("Positions"+cfg.internalSeparator+self.defaultColumn)   
            self.defaultColumnAdded = True     
        
    def __sendSampTable(self):  
        self.__appendMeshColumns()
        isDouble = True
        if self.precision == cfg.floatPrecision:
            isDouble = False
        filename = os.path.expanduser("~/.extractor.xml")
        hdf.Exporter.exportAsVotable(self.hdfData, self.exportedDataHeader, self.exportedData, filename, isDouble)
        self.sampWidget.sendTable(filename)
        
        
        
    def __switchMenuState(self, value):
        """
            Toggle on or off the script menu button
        """
        
        if value is True : 
            self.menuButton.menu.entryconfig(2, state=tk.NORMAL)
            self.exportMenuButton.menu.entryconfig(1, state=tk.NORMAL)
        else : 
            self.menuButton.menu.entryconfig(2, state=tk.DISABLED)
            self.exportMenuButton.menu.entryconfig(1, state=tk.DISABLED)
            
    def onDelete(self):
        if  self.sampWidget.client.isConnected():   
            try : 
                self.sampWidget.client.disconnect()
            except Exception as e:
                print e.value
        self.root.quit()  
