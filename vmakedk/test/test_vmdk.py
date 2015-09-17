import unittest

from vmakedk.vmdk import sectors_to_geometry

class TestGeometry(unittest.TestCase):
    """test some disk sizes match geometry created with ESXi 6.0
    """

    def test_less_than_1gb(self):
        heads, spt, cylinders = sectors_to_geometry(409600)
        self.assertEquals(heads, 64)
        self.assertEquals(spt, 32)
        self.assertEquals(cylinders, 200)

    def test_greater_than_1gb_and_less_than_2gb(self):
        heads, spt, cylinders = sectors_to_geometry(3276800)
        self.assertEquals(heads, 128)
        self.assertEquals(spt, 32)
        self.assertEquals(cylinders, 800)

    def test_greater_than_2gb(self):
        heads, spt, cylinders = sectors_to_geometry(4915200)
        self.assertEquals(heads, 255)
        self.assertEquals(spt, 63)
        self.assertEquals(cylinders, 305)

    def test_16gb(self):
        heads, spt, cylinders = sectors_to_geometry(33554432)
        self.assertEquals(heads, 255)
        self.assertEquals(spt, 63)
        self.assertEquals(cylinders, 2088)

if __name__ == '__main__':
    unittest.main()

