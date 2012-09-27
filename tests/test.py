import sys
sys.path.append('../')
import unittest
import hdf
import convert
import config as cfg
import votable as vot

class TestPointerFactory(unittest.TestCase):
    def setUp(self):
        factory = hdf.PointerFactory()
        factory.withPath('path').withDataset('dataset')
        factory.withName('name').withColumn('column').withUnit('unit')
        factory.withUcd('ucd').withSkos('skos').withUtype('utype')
        factory.withDescription('description')
        self.pointer = factory.getPointer()      
     
    def test_getPointer(self):
        self.assertTrue(self.pointer.path=='path')
        self.assertTrue(self.pointer.dataset=='dataset')
        self.assertTrue(self.pointer.name=='name')
        self.assertTrue(self.pointer.column=='column')
        self.assertTrue(self.pointer.unit=='unit')
        self.assertTrue(self.pointer.ucd=='ucd')
        self.assertTrue(self.pointer.skos=='skos')
        self.assertTrue(self.pointer.utype=='utype')
        self.assertTrue(self.pointer.description=='description')
        
class TestPointer(unittest.TestCase):     
    def test_getPointer(self):
        p = hdf.Pointer()
        self.assertTrue(p.path is None)
        self.assertTrue(p.dataset is None)
        self.assertTrue(p.name is None)
        self.assertTrue(p.column is None)
        self.assertTrue(p.unit is None)
        self.assertTrue(p.ucd is None)
        self.assertTrue(p.skos is None)
        self.assertTrue(p.utype is None)
        self.assertTrue(p.description is None)
        
class TestConversion(unittest.TestCase):
    def test_float(self):        
        result = str(convert.getValue(1.0, cfg.floatPrecision))
        self.assertTrue(result == '1.000000e+00')
        
    def test_double(self):        
        result = str(convert.getValue(1.0, cfg.doublePrecision))
        self.assertTrue(result == '1.000000000000000e+00')
        
class TestPdrHDF(unittest.TestCase):
    def setUp(self):
        self.hdf = hdf.PdrHDF('test_file.hdf5')
        
    def test_defaultcolumn(self):
        result = self.hdf.getDefaultColumns()
        self.assertTrue(len(result) == 3)
        self.assertTrue('tau_V' in result)
        self.assertTrue('distance' in result)
        self.assertTrue('AV' in result)
        
    def test_getByGroup(self):
        group = self.hdf.getByGroup('/CloudStructure/Abundances')
        dataset = group['Abundances'][0]
        self.assertTrue(len(dataset) == 137)
        
    def test_index(self):
        pointer = self.hdf.index['Abundances']['n(C)']        
        self.assertTrue(pointer.name == 'n(C)')
        self.assertTrue(pointer.path == '/CloudStructure/Abundances')
        self.assertTrue(pointer.dataset == 'Abundances')
        self.assertTrue(pointer.column == '3')
        self.assertTrue(pointer.unit == 'cm-3')
        self.assertTrue(pointer.ucd == 'none')
        self.assertTrue(pointer.skos == 'http://purl.org/astronomy/vocab/PhysicalQuantities/AbundanceOfOKTJSMMVPCPJKN-UHFFFAOYSA-N')
        self.assertTrue(pointer.utype == 'none')
        self.assertTrue(pointer.description == 'No description')    
        
    def test_extractQuantity(self):
        pointer = self.hdf.index['Abundances']['n(C)'] 
        data = self.hdf.extractQuantity(pointer)
        self.assertTrue(len(data) == 413)
        self.assertTrue(data[0] == 0.00066791594955656667)
        
class TestFieldFactory(unittest.TestCase):
    def setUp(self):
        builder = vot.FieldBuilder()
        builder.withName('name').withUcd('ucd')
        builder.withUtype('utype').withUnit('unit')
        builder.withId('id').withDatatype('datatype')
        builder.withArraysize('arraysize').withWidth('width')
        builder.withPrecision('precision').withXtype('xtype')
        builder.withRef('ref')
        self.field = builder.getField()
        
    def test_getField(self):
        self.assertTrue(self.field.name == 'name')
        self.assertTrue(self.field.ucd == 'ucd')
        self.assertTrue(self.field.utype == 'utype')
        self.assertTrue(self.field.unit == 'unit')
        self.assertTrue(self.field.id == 'id')
        self.assertTrue(self.field.datatype == 'datatype')
        self.assertTrue(self.field.arraysize == 'arraysize')
        self.assertTrue(self.field.width == 'width')
        self.assertTrue(self.field.precision == 'precision')
        self.assertTrue(self.field.xtype == 'xtype')
        self.assertTrue(self.field.ref == 'ref')
        
class TestField(unittest.TestCase):
    def test_getField(self):
        field = vot.Field()
        self.assertTrue(field.name is None)
        self.assertTrue(field.ucd is None)
        self.assertTrue(field.utype is None)
        self.assertTrue(field.unit is None)
        self.assertTrue(field.id is None)
        self.assertTrue(field.datatype is None)
        self.assertTrue(field.arraysize is None)
        self.assertTrue(field.width is None)
        self.assertTrue(field.precision is None)
        self.assertTrue(field.xtype is None)
        self.assertTrue(field.ref is None)
        
    def test_toString(self):
        field = vot.FieldBuilder().withName('name').getField()
        self.assertTrue(field.toString() == '<FIELD name="name" />')
    
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestPointerFactory('test_getPointer'))
    suite.addTest(TestPointer('test_getPointer'))
    suite.addTest(TestConversion('test_float'))
    suite.addTest(TestConversion('test_double'))
    suite.addTest(TestPdrHDF('test_defaultcolumn'))
    suite.addTest(TestPdrHDF('test_getByGroup'))
    suite.addTest(TestPdrHDF('test_index'))
    suite.addTest(TestPdrHDF('test_extractQuantity'))
    suite.addTest(TestFieldFactory('test_getField'))
    suite.addTest(TestField('test_getField'))
    suite.addTest(TestField('test_toString'))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
        

