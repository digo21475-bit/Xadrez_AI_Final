import pytest
from training.batch_sampler import count_tokens_in_batch, adjust_batch_size, DynamicBatchSampler


def fake_batch_gen_factory(state_size_tokens):
    def gen(n):
        # return n items where each item represents a state
        for i in range(n):
            yield ('state', )
    return gen


def test_count_tokens_empty():
    assert count_tokens_in_batch([]) == 0


def test_adjust_batch_size_simple():
    # simulate tokens such that each item is 832 tokens
    def batch_gen(n):
        return [None] * n

    best = adjust_batch_size(16, max_tokens=832 * 4, batch_gen=batch_gen, verbose=False)
    assert best == 4


def test_dynamic_batch_sampler_trims():
    class Buf:
        def __init__(self, items):
            self.items = items
        def sample(self, n):
            return self.items[:n]

    # create 10 items -> tokens = 10 * 832 > max_tokens 5*832
    items = [None] * 10
    buf = Buf(items)
    sampler = DynamicBatchSampler(buf, initial_batch_size=10, max_tokens=832 * 5)
    batch = sampler.sample()
    # should trim to at most 5 items
    assert len(batch) <= 5
