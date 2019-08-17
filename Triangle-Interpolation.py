'''
Created on Jul 17, 2019

@author: anshul
'''
import numpy as np
import Gravity
import pandas as pd

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
def barycentric_weights(P, A, B, C):
    AB = (B.x - A.x, B.y - A.y)
    AC = (C.x - A.x, C.y - A.y)
    AP = (P.x - A.x, P.y - A.y)
    d00 = np.dot(AB, AB)
    d01 = np.dot(AB, AC)
    d11 = np.dot(AC, AC)
    d20 = np.dot(AP, AB)
    d21 = np.dot(AP, AC)

    denom = d00 * d11 - d01 * d01
    v = (d11 * d20 - d01 * d21) / denom
    w = (d00 * d21 - d01 * d20) / denom
    u = 1.0 - v - w
    return [u, v, w]

def create_visual(game, time):
    vectorDict = Gravity.get_vectors()
    momentList = vectorDict[game]
    for d in momentList:
        if max(d.keys()) == time:
            poss = d
    d = {}
    d['time'] = []
    for time, moment in poss.items():
        d['time'].append(time)
        for k, v in moment.items():
            defender, A, B, C = v[0], v[1], v[2], v[3]
            if k not in d:
                d[k] = []
            weightA, weightB, weightC = barycentric_weights(defender, A, B, C)
            if weightA < 0.0:
                x_diff = defender.x - A.x
                y_diff = defender.y - A.y
                A.x += (2*x_diff)
                A.y += (2*y_diff)
                weightA = barycentric_weights(defender, A, B, C)
            
            
            d[k].append(weight[0])
        
    df = pd.DataFrame(d)
    #df.to_csv("poss_test_14.csv")
    #df = df.round(5)
    print(df)

if __name__ == '__main__':
    game = 20141115
    time = 494.93
    create_visual(game, time)
    """a = Coordinate(5, 8)
    b = Coordinate(5, 5)
    c = Coordinate(8, 5)
    p = Coordinate(5, 7)
    print(barycentric_weights(p, a, b, c))"""