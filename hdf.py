'''
Notes :

PS: Table Metadata :
 Metadata contains :
PathHDF5 | DataSet | Col.Index | PubID | HName  | DataType | Unit | SKOS | UCD | utype | Description | ObjParent | Group |
   0     |    1    |     2     |   3   |   4    |    5     |  6   |  7   |  8  |  9    |   10        |    11     |  12   |
   
 Metadata_ObjType contains :
 PubID | Hname | SKOS | Description

'''
import h5py as h5
import votable as vot
import numpy as numpy
import memory as m
import config as cfg
import convert as conv


__author__ = "Nicolas Moreau"
__copyright__ = "Copyright 2012"
__credits__ = ["Nicolas Moreau"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Nicolas Moreau"
__email__ = "nicolas.moreau@obspm.fr"
__status__ = "Development"  


class PointerFactory(object):
    def __init__(self):
        self.pointer = Pointer()
        
    def withPath(self, path):
        self.pointer.path = path
        return self

    def withDataset(self, dataset):
        self.pointer.dataset = dataset
        return self        
        
    def withName(self, name):
        self.pointer.name = name
        return self
        
    def withColumn(self, column):
        self.pointer.column = column
        return self
        
    def withUnit(self, unit):
        self.pointer.unit = unit
        return self
        
    def withUcd(self, ucd):
        self.pointer.ucd = ucd
        return self
        
    def withSkos(self, skos):
        self.pointer.skos = skos
        return self
        
    def withUtype(self, utype):
        self.pointer.utype = utype
        return self
        
    def withDescription(self, description):
        self.pointer.description = description
        return self
        
    def withObjParent(self, parent):
        self.pointer.objParent = parent
        return self
        
    def withGroup(self, group):
        self.pointer.group = group
        return self
        
    def getPointer(self):
        return self.pointer
    
class Pointer(object):
    """
        Points on data in a dataset
    """
    def __init__(self):
        #dataset path
        self.path = None
        #dataset name
        self.dataset = None
        #quantity human readable name
        self.name = None
        #column position in dataset
        self.column = None
        self.ucd = None
        self.skos = None
        self.utype = None
        self.unit = None
        self.description = None
        self.objParent = None
        self.group = None

  
class PdrHDF(object):
    """
        Access to a pdr HDF5 file
    """
    def __init__(self, filename):
        #hdf file
        self.f =  h5.File(filename, 'r')
        #create a pivoted array with the metadata
        self.metadata = numpy.array(self.f['/Metadata/MetaData'])
        #indexes all the data
        #index[dataset_name][column_name] = pointer
        self.index = self.__buildIndex()
        
    def close(self):
        """
            close hdf file
        """
        self.f.close()
        
    def getByGroup(self, group):
        """
            returns the object located at group position
        """
        try : 
            return self.f[group]
        except KeyError:
            print "group : " +group+ " not found"       
            
    def getDefaultColumns(self):
        result = []
        for key in  self.index['Positions']:
            result.append(key)
        return result
            
            
    def __buildIndex(self):
        """
            creates the index
        """        
        datasets = {}
        for line in self.metadata:
            if line[1] not in datasets : 
                datasets[line[1]] = {}   
            pf = PointerFactory()
            pf.withPath(line[0]).withDataset(line[1])
            pf.withName(line[4]).withColumn(line[2])
            pf.withUnit(line[6]).withUcd(line[8])
            pf.withSkos(line[7]).withUtype(line[9])
            pf.withDescription(line[10]).withObjParent(line[11])
            pf.withGroup(line[12]).getPointer()
            datasets[line[1]][line[4]] = pf.getPointer()
        return datasets
        
    def extractQuantity(self, p):  
        """
            extract a quantity according to the pointer p
        """
        ds = self.f[p.path+'/'+p.dataset]
        #1D array, returned directly
        if len(ds.shape) == 1:
            return ds
        else :        
            return [row[int(p.column)] for row in ds]
 
        
class Writer(object):
    """
        write extracted data in a file
    """
    def __init__(self, filename, header=None, separator=',', isdouble=False):
        #output file name
        self.filename = filename
        #a list of pointers
        self.pointers = []
        #a list of columns
        self.columns = []
        #separator between values
        self.separator = separator
        #
        self.header = header
        # precision is .6 if False, .15 if True
        self.isDouble = isdouble
        
        
        
    def addColumn(self, pointer, column):
        """
            add a column of data and its pointer
        """
        self.pointers.append(pointer)
        self.columns.append(column)
        
    def clearColumns(self):
        self.pointers = []
        self.columns = []
        
    def write(self):
        """
            write all data
        """        
        try:
            precision = "float"
            if self.isDouble:
                precision = "double"
            self.__columnsAreWritable()
            f = open(self.filename, 'w')
            result = ''
            if self.header is not None :
                result += "".join(self.header)
            result += '#'
            for pointer in self.pointers : 
                result+=pointer.name+self.separator
            f.write(result[0:len(result)-1]+"\n")
            size = len(self.columns[0])
            
            for i in range(0, size):                
                values = [column[i] for column in self.columns]                
                size = len(values)          
                if isinstance(values[0],numpy.string_) is False:
                    f.write(self.separator.join([conv.getValue(el, precision) for el in values]))
                else:
                    f.write(self.separator.join(values))
                f.write("\n")              
            f.close()
        except Exception as e:
            print e
                
        
    def __columnsAreWritable(self):
        """
            check data validity
        """
        if len(self.columns) != len(self.pointers):
            raise Exception("columns and pointers do not match")
        
        if len(self.columns) > 0 :
            size = len(self.columns[0])
            for i in range(1, len(self.columns)):
                if len(self.columns[i]) != size:
                    raise Exception('all the columns do not have the same size')
            return True        
        raise Exception("no data")
        
class Exporter(object):
    @staticmethod
    def exportAsText(hdf5, header, columns, outputfile, separator=",", isdouble=False): 
        """
        export selected data into text file
        """      
        w = Writer(outputfile, header, separator, isdouble)
        for i in range(0,len(columns)):
            parts = columns[i].split(cfg.internalSeparator)
            w.addColumn(hdf5.index[parts[0]][parts[1]], hdf5.extractQuantity(hdf5.index[parts[0]][parts[1]]))
        w.write()
        
    @staticmethod
    def exportAsVotable(hdf5, header, columns, outputfile, isdouble=False): 
        """
        export selected data into text file
        """        
        table = vot.Votable()        
        datatype='float'
        if isdouble : 
            datatype = 'double'
        for i in range(0,len(columns)):
            parts = columns[i].split(cfg.internalSeparator)
            builder = vot.FieldBuilder()
            field = hdf5.index[parts[0]][parts[1]]
            link = vot.LinkBuilder().withContentRole('type').withHref(field.skos).getLink()
            table.addField(builder.withName(field.name).withUnit(field.unit).withUcd(field.ucd).withUtype(field.utype).withDatatype(datatype).withLink(link).getField())
            table.addColumn(hdf5.extractQuantity(hdf5.index[parts[0]][parts[1]]))
        table.toFile(outputfile)

