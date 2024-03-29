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

  def test_contiguous_ranges(self):
    from .device import find_contiguous_ranges

    self.assertEqual(
      list(find_contiguous_ranges([1,2,5,6,7], max_delta=1, singles=[])),
      [[1,2], [5,6,7]])

    self.assertEqual(
      list(find_contiguous_ranges([1,2,5,6,7], max_delta=1, singles=[5])),
      [[1,2], [5], [6,7]])

    self.assertEqual(
      list(find_contiguous_ranges([1,2,5,6,7], max_delta=3, singles=[])),
      [[1,2,5,6,7]])

    self.assertEqual(
      list(find_contiguous_ranges([1,2,5,6,7], max_delta=3, singles=[2])),
      [[1],[2],[5,6,7]])

if __name__ == '__main__':
  unittestmain()
