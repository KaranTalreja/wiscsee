import unittest


from accpatterns.patterns import *
from accpatterns.contractbench import *


class TestAlignment(unittest.TestCase):
    def test_init(self):
        alignbench = Alignment(block_size=128*KB, space_size=128*MB,
                aligned=True, op=OP_WRITE)
        alignbench = Alignment(block_size=128*KB, space_size=128*MB,
                aligned=False, op=OP_READ)

    def test_aligned(self):
        alignbench = Alignment(block_size=4, space_size=12,
                aligned=True, op=OP_WRITE)

        reqs = list(alignbench)
        self.assertEqual(len(reqs), 6)

        offs = [req.offset for req in reqs]
        self.assertListEqual(offs, [0, 2, 4, 6, 8, 10])

        for req in reqs:
            self.assertEqual(req.op, OP_WRITE)
            self.assertEqual(req.size, 2)

    def test_unaligned(self):
        alignbench = Alignment(block_size=4, space_size=12,
                aligned=False, op=OP_WRITE)

        reqs = list(alignbench)
        self.assertEqual(len(reqs), 6)

        offs = [req.offset for req in reqs]
        self.assertListEqual(offs, [2, 0, 6, 4, 10, 8])

        for req in reqs:
            self.assertEqual(req.op, OP_WRITE)
            self.assertEqual(req.size, 2)


class TestRequestScale(unittest.TestCase):
    def test_init(self):
        reqbench = RequestScale(space_size=128*MB, chunk_size=4*KB,
                traffic_size=8*MB, op=OP_WRITE)

    def test_scale(self):
        bench = RequestScale(space_size=10, chunk_size=2,
                traffic_size=20, op=OP_WRITE)

        reqs = list(bench)

        offs = [req.offset for req in reqs]

        self.assertEqual(len(reqs), 10)

        for req in reqs:
            self.assertEqual(req.op, OP_WRITE)
            self.assertEqual(req.size, 2)


class TestGroupByInvTimeAtAccTime(unittest.TestCase):
    def test_init(self):
        bench = GroupByInvTimeAtAccTime(space_size=128*MB, traffic_size=128*MB,
                chunk_size=4*KB, grouping=True)

    def test_group_by_time(self):
        bench = GroupByInvTimeAtAccTime(space_size=32, traffic_size=4,
                chunk_size=2, grouping=True)

        reqs = list(bench)
        self.assertEqual(len(reqs), 6)

        offs = [req.offset for req in reqs]
        self.assertListEqual(offs, [0, 2, 28, 30, 0, 2])

        ops = [req.op for req in reqs]
        self.assertListEqual(ops, [OP_WRITE, OP_WRITE, OP_WRITE, OP_WRITE,
            OP_DISCARD, OP_DISCARD])

        for req in reqs:
            self.assertEqual(req.size, 2)

    def test_not_group_by_time(self):
        bench = GroupByInvTimeAtAccTime(space_size=32, traffic_size=4,
                chunk_size=2, grouping=False)

        reqs = list(bench)
        self.assertEqual(len(reqs), 6)

        offs = [req.offset for req in reqs]
        self.assertListEqual(offs, [0, 28, 2, 30, 0, 2])

        ops = [req.op for req in reqs]
        self.assertListEqual(ops, [OP_WRITE, OP_WRITE, OP_WRITE, OP_WRITE,
            OP_DISCARD, OP_DISCARD])

        for req in reqs:
            self.assertEqual(req.size, 2)


class TestGroupInvTimeInSpace(unittest.TestCase):
    def test_init(self):
        bench = GroupByInvTimeInSpace(space_size=128*MB, traffic_size=128*MB,
                chunk_size=4*KB, grouping=True)

    def test_group_at_space(self):
        bench = GroupByInvTimeInSpace(space_size=32, traffic_size=4,
                chunk_size=2, grouping=True)

        reqs = list(bench)
        self.assertEqual(len(reqs), 6)

        offs = [req.offset for req in reqs]
        self.assertListEqual(offs, [0, 28, 2, 30, 0, 2])

        ops = [req.op for req in reqs]
        self.assertListEqual(ops, [OP_WRITE, OP_WRITE, OP_WRITE, OP_WRITE,
            OP_DISCARD, OP_DISCARD])

        for req in reqs:
            self.assertEqual(req.size, 2)

    def test_not_group_at_space(self):
        bench = GroupByInvTimeInSpace(space_size=32, traffic_size=4,
                chunk_size=2, grouping=False)

        reqs = list(bench)
        self.assertEqual(len(reqs), 6)

        offs = [req.offset for req in reqs]
        self.assertListEqual(offs, [0, 2, 4, 6, 0, 4])

        ops = [req.op for req in reqs]
        self.assertListEqual(ops, [OP_WRITE, OP_WRITE, OP_WRITE, OP_WRITE,
            OP_DISCARD, OP_DISCARD])

        for req in reqs:
            self.assertEqual(req.size, 2)



def main():
    unittest.main()

if __name__ == '__main__':
    main()

