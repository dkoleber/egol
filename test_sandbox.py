import numpy as np


if __name__ == '__main__':
    test1 = [6,1,2,6,8,3,4,0,6,1,62,1]
    test2 = [[5,2],[6,2],[4,0],[0,7]]
    test3 = [[test2 for x in range(3)] for y in range(3)]


    arr = np.asarray(test1) == -1
    print(arr)
    print(np.argmin(arr==0))

    arr2 = np.asarray(test2)
    arr2 = arr2 == 0
    print(arr2)
    m1 = np.argmin(arr2,axis=1)
    print(m1)
    m2 = np.argmax(m1)
    print(m2)

    arr3 = np.asarray(test2)
    d1 = np.delete(arr3,0,axis=1)
    print(d1)

    print('------')

    arr4 = np.asarray(test3)
    print(arr4)
    d2 = np.delete(arr4,0,axis=3)
    print(d2)
    c1,c2 = np.unique(d2, return_counts=True)
    c3 = dict(zip(c1,c2))
    print(c3)
    print(c1[c2.argmax()])
