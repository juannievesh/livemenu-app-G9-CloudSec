from app.core.rate_limit import RateLimitMiddleware


def test_rate_limit_allows_under_limit():
    mw = RateLimitMiddleware.__new__(RateLimitMiddleware)
    mw.requests_per_minute = 5
    from collections import defaultdict
    mw._storage = defaultdict(list)

    for _ in range(5):
        assert mw._is_allowed("127.0.0.1") is True


def test_rate_limit_blocks_over_limit():
    mw = RateLimitMiddleware.__new__(RateLimitMiddleware)
    mw.requests_per_minute = 3
    from collections import defaultdict
    mw._storage = defaultdict(list)

    for _ in range(3):
        mw._is_allowed("127.0.0.1")

    assert mw._is_allowed("127.0.0.1") is False


def test_rate_limit_different_ips():
    mw = RateLimitMiddleware.__new__(RateLimitMiddleware)
    mw.requests_per_minute = 2
    from collections import defaultdict
    mw._storage = defaultdict(list)

    mw._is_allowed("10.0.0.1")
    mw._is_allowed("10.0.0.1")
    assert mw._is_allowed("10.0.0.1") is False
    assert mw._is_allowed("10.0.0.2") is True
