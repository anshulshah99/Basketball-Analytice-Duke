# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:56:35 2019

@author: schmi
"""
import numpy as np
import itertools as it

pairDistDict = {}

def inefficientPairs(offList = None,defList = None):
    pairs = []
    offPlayers = range(5)
    defPlayers = range(5)
    bestOPermute = [-1, -1, -1, -1, -1]
    bestDPermute = [-1, -1, -1, -1, -1]
    currMin = 1e6
    for o in it.permutations(offPlayers):
        for d in it.permutations(defPlayers):
            thisMin = 1e7
            for i in range(len(o)):
                thisMin = thisMin + pairDistDict.get((d[i],o[i]))
            if(thisMin < currMin):
                bestOPermute = o
                bestDPermute = d
                currMin = thisMin
    if(bestOPermute[0] == -1):
        raise RuntimeError("Failed to find a permutation.")
                #pairs.append((d[i],o[i]))
    for k in range(len(bestOPermute)):
        pairs.append(bestDPermute[k],bestOPermute[k])
    return pairs
    