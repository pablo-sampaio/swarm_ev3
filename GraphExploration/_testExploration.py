
from Exploration import *



def TEST1():
    ''' Some tests with differente representations of NavigationData 
    '''
    for example in [b"[AABBCCDD,11223344,33224455]45",
               b"[AABBCCDD,11223344,33224455]37(AABBCCDD,3)"]:
        print("EXAMPLE OF BYTES:", example)
        navdata = NavigationData()
        navdata.parseFrom(example)

        representation = str(navdata)
        print("- print:      ", representation, ", type:", type(representation), ", len:", len(representation))
        representation = navdata.toBytes()
        print("- toBytes:    ", representation, ", type:", type(representation), ", len:", len(representation))
        representation = navdata.toBytes().hex()
        print("- toBytes.hex:", representation, ", type:", type(representation), ", len:", len(representation))


def TEST2():
    ''' Tests ExplorationManagerDfs3Simpl by simulating navigation in a graph
    only to confirm if the next visits are properly indicated by this class 
    '''
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


TEST1()
#TEST2()