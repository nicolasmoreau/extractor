import convert as conv

class FieldBuilder(object):
    def __init__(self):
        self.field = Field()
        
    def withName(self, name):
        self.field.name = name
        return self
        
    def withUcd(self, ucd):
        self.field.ucd = ucd
        return self
        
    def withUtype(self, utype):
        self.field.utype = utype
        return self
        
    def withUnit(self, unit):
        self.field.unit = unit
        return self
        
    def withId(self, fid):
        self.field.id = fid
        return self
        
    def withDatatype(self, datatype):
        self.field.datatype = datatype
        return self
        
    def withArraysize(self, arraysize):
        self.field.arraysize = arraysize
        return self
        
    def withWidth(self, width):
        self.field.width = width
        return self
        
    def withPrecision(self, prec):
        self.field.precision = prec
        return self
        
    def withXtype(self, xtype):
        self.field.xtype = xtype
        return self
    
    def withRef(self, ref):
        self.field.ref = ref
        return self
    
    def getField(self):
        return self.field
    
        
    

class Field(object):
    def __init__(self):
        self.name = None
        self.ucd = None
        self.utype = None
        self.unit = None
        self.id = None
        self.datatype = None
        self.arraysize = None
        self.width = None
        self.precision = None
        self.xtype = None
        self.ref = None
        
    def toString(self):
        result = '<FIELD'
        
        if self.name is not None : 
            result += ' name="'+self.name+'" '

        if self.ucd is not None : 
            result += ' ucd="'+self.ucd+'" '
            
        if self.utype is not None : 
            result += ' utype="'+self.utype+'" '
            
        if self.unit is not None : 
            result += ' unit="'+self.unit+'" '
            
        if self.id is not None : 
            result += ' id="'+self.id+'" '
            
        if self.datatype is not None : 
            result += ' datatype="'+self.datatype+'" '

        if self.arraysize is not None : 
            result += ' arraysize="'+self.arraysize+'" '
            
        if self.width is not None : 
            result += ' width="'+self.width+'" '

        if self.precision is not None : 
            result += ' precision="'+self.precision+'" '
            
        if self.xtype is not None : 
            result += ' xtype="'+self.xtype+'" '
    
        if self.ref is not None : 
            result += ' ref="'+self.ref+'" '
        
        return result+'/>'
        

class Votable(object):
    def __init__(self):
        self.fields = []
        self.columns = []
        
    def addField(self, field):
        if isinstance(field, Field):
            self.fields.append(field)
            
    def addColumn(self, data):
        self.columns.append(data)
        
        
    def getTable(self):
        result = '<?xml version="1.0"?>'
        result += '<VOTABLE version="1.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.ivoa.net/xml/VOTable/v1.2">'+"\n"
        result += '<RESOURCE name="PdrExporter">'+"\n"
        result += '<TABLE name="results">'+"\n"
        
        for field in self.fields : 
            result += field.toString()+"\n"
            
        result += '<DATA>'+"\n"
        result += '<TABLEDATA>'+"\n"         
         
        columns_size = len(self.columns)
        data_size = len(self.columns[0])
        for i in range(0, data_size):        
            result += '<TR>'+"\n"            
            for j in range(0, columns_size):
                result += '<TD>'+str(conv.getValue(self.columns[j][i], self.fields[j].datatype))+'</TD>'+"\n"
            result += '</TR>'+"\n"
            
        result += '</TABLEDATA>'+"\n"
        result += '</DATA>'+"\n"
        
        result += '</TABLE>'+"\n"
        result += '</RESOURCE>'+"\n"
        
        result += '</VOTABLE>'
        return result        
        
    '''def __getValue(self, value, vtype):
        if vtype == "double":
            return "%.15e"%value
        elif vtype == "float":
            return "%.6e"%value
        else:
            return value
    '''
        
    def toFile(self, filename):        
        f = open(filename, 'w')
        f.write(self.getTable())
        f.close()         
