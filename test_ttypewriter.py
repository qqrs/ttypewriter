import py.test
from ttypewriter import lookup_key, calc_seppoints, calc_keypress_avg, median, average

def test_lookup_key():
    keycodes = [(10,'a'), (20,'b'), (31, 'c')]
    seps = [15, 25]

    assert(lookup_key(keycodes, seps, 0) == 'a')
    assert(lookup_key(keycodes, seps, 10) == 'a')
    assert(lookup_key(keycodes, seps, 15) == 'a')

    assert(lookup_key(keycodes, seps, 16) == 'b')
    assert(lookup_key(keycodes, seps, 25) == 'b')

    assert(lookup_key(keycodes, seps, 26) == 'c')
    assert(lookup_key(keycodes, seps, 40) == 'c')
    assert(lookup_key(keycodes, seps, 1023) == 'c')

    with py.test.raises(ValueError):
        lookup_key(keycodes, seps, -1)
    with py.test.raises(ValueError):
        lookup_key(keycodes, seps, 10241)

def test_calc_seppoints():
    keycodes = [(10,'a'), (20,'b'), (31, 'c')]
    seps = [15, 25]
    assert(calc_seppoints(keycodes) == seps)

def test_calc_keypress_avg():
    assert(calc_keypress_avg([10,10,10], 0.10) != 0)
    assert(calc_keypress_avg([10,10]   , 0.10) == 0)
    assert(calc_keypress_avg([10,10,10], 0.09) == 0)

    assert(calc_keypress_avg([100,104,103], 0.10) == 102)
    assert(calc_keypress_avg([100,104,103, 999], 0.10) == 102)

def test_median():
    assert(median([10,12,11]) == 11)

def test_average():
    assert(average([10,100]) == 55)
    assert(average([10,101]) == 55)
