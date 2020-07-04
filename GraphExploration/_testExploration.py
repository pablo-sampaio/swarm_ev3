
from Exploration import *


def TEST1():
    for example in [b"[AABBCCDD,11223344,33224455]45",
               b"[AABBCCDD,11223344,33224455]37(AABBCCDD,3)"]:
        print("EXAMPLE OF BYTES:", example)
        navdata = NavigationData()
        navdata.parseFrom(example)

        print("-", navdata)
        print("-", navdata.toBytes())
        print("-", navdata.toBytes().hex())


def TEST2():
    exp = ExplorationManagerDfs3Simpl() #ExplorationManagerDfs3()

    x = NavigationData()
    x.setup(3)
    x.new = True

    print("proximo:", exp.nextNode('x', x))
    x.new = False

    y = NavigationData()
    y.setup(1)
    print("proximo:", exp.nextNode('y', y))
    y.new = False

    print("proximo: ", exp.nextNode('x', x))

    z = NavigationData()
    z.setup(2)
    print("proximo:", exp.nextNode('z', z))
    z.new = False

    w = NavigationData()
    w.setup(2)
    print("proximo:", exp.nextNode('w', w))
    w.new = False

    print("proximo:", exp.nextNode('x', x))

    print("proximo:", exp.nextNode('w', w))

    print("proximo:", exp.nextNode('z', z))

    print("proximo:", exp.nextNode('x', x))

    print("proximo:", exp.nextNode('w', w))

    print("proximo:", exp.nextNode('x', x))


TEST2()