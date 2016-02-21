import unittest

import FtlSim


class Test_translation_cache(unittest.TestCase):
    def test1(self):
        lrucache = FtlSim.lrulist.LruCache()
        lrucache[1] = 11
        lrucache[2] = 22
        lrucache[3] = 33
        print lrucache
        print lrucache.least_recently_used_key()
        print lrucache.most_recently_used_key()
        self.assertEqual(lrucache.least_recently_used_key(), 1)
        self.assertEqual(lrucache.most_recently_used_key(), 3)
        lrucache[2] = 222
        self.assertEqual(lrucache.most_recently_used_key(), 2)
        self.assertEqual(lrucache.peek(1), 11)
        # peek should not change order
        self.assertEqual(lrucache.most_recently_used_key(), 2)

        lrucache.orderless_update(1, 111)
        self.assertEqual(lrucache.most_recently_used_key(), 2)
        self.assertEqual(lrucache.peek(1), 111)


def main():
    unittest.main()

if __name__ == '__main__':
    main()





