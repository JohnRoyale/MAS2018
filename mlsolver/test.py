from mlsolver.kripke_model import WiseMenWithHat, TheShipThreeAgents, TheShipNAgents
from mlsolver.formula import *
import timeit

def test_wmwh():
    wmwh = WiseMenWithHat()
    ks = wmwh.ks
    ks.print()
    ks = ks.solve(wmwh.knowledge_base[1])
    ks.print()

# Small test with the 3-agent The Ship Kripke model
def test_ts3():
    # Init the model
    ts3 = TheShipThreeAgents()
    ks = ts3.ks
    # Print initial model
    ks.print()

    # Check whether (M,312) |= K_1 t13
    # t13 is true in the only world accessible from 312 by 1, so it should return True
    f = Box_a('1', Atom('t13'))
    print("(M,312) |= K_1 t13: ", f.semantic(ks, '312'))
    print()

    # Check whether (M,312) |= K_1 t12
    # t12 is false in the only world accessible from 312 by 1, so it should return False
    f = Box_a('1', Atom('t12'))
    print("(M,312) |= K_1 t12: ", f.semantic(ks, '312'))
    print()

    # Suppose that everyone suddenly knows that 1 targets 3.
    # Now, everyone knows their target, so the entire model collapses to one state
    f = Box_star(Atom('t13'))
    ks = ks.solve(f)
    ks.print()

def test_tsn():
    start = timeit.default_timer()
    tsn = TheShipNAgents(3)
    stop = timeit.default_timer()
    print("\nTime needed to build worlds: ", stop - start)


    ks = tsn.ks
    f = Box_a('1', Atom('t13'))
    print("(M,312) |= K_1 t13: ", f.semantic(ks, '312'))
    print()

#test_ts3()
test_tsn()