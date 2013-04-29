from ttypewriter import lookup_key

def test_lookup_key():
    keycodes = [(10,'a'), (20,'b'), (30, 'c')]
    seps = [15, 25]
    assert(lookup_key(keycodes, seps, 10) == 'a')
