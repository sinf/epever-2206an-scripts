from unittest import TestCase, main as unittestmain

class TestDing(TestCase):
  def setUp(self):
    pass
  
  def test_foo(self):
    self.assertEqual(True,True)

  def test_bitlist(self):
    from .fake_client import bitlist
    self.assertEqual(bitlist(0), [0])
    self.assertEqual(bitlist(1), [1])
    self.assertEqual(bitlist(2), [0,1])
    self.assertEqual(bitlist(4), [0,0,1])
    self.assertEqual(bitlist(0xAB), [1,1,0,1,0,1,0,1])

if __name__ == '__main__':
  unittestmain()
