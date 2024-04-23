from paths_cli.utils import *

class TestOrderedSet:
    def setup_method(self):
        self.set = OrderedSet(['a', 'b', 'a', 'c', 'd', 'c', 'd'])

    def test_len(self):
        assert len(self.set) == 4

    def test_empty(self):
        ordered = OrderedSet()
        assert len(ordered) == 0
        for _ in ordered:  # -no-cov-
            raise RuntimeError("This should not happen")

    def test_order(self):
        for truth, beauty in zip("abcd", self.set):
            assert truth == beauty

    def test_add_existing(self):
        assert len(self.set) == 4
        self.set.add('a')
        assert len(self.set) == 4
        assert list(self.set) == ['a', 'b', 'c', 'd']

    def test_contains(self):
        assert 'a' in self.set
        assert not 'q' in self.set
        assert 'q' not in self.set

    def test_discard(self):
        self.set.discard('a')
        assert list(self.set) == ['b', 'c', 'd']

    def test_discard_add_order(self):
        assert list(self.set) == ['a', 'b', 'c', 'd']
        self.set.discard('a')
        self.set.add('a')
        assert list(self.set) == ['b', 'c', 'd', 'a']

