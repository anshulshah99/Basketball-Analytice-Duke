# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 10:43:22 2019

@author: schmi
"""
import numpy as np
import matplotlib.pyplot as plt

def error(predicted,actual):
    return abs(predicted - actual) / predicted * 100

actualVals = [81,235,310,276,330,328]
predictedVals = [[81,235,310,276,330,328],
                 [74.25,241.82,305.23,258.54,351.81,342.58],
                 [102.27,186.67,293.68,265.14,252.22,324.55],
                 [69.18,342.75,321.53,253.64,553.09,391.31],
                 [82.59,240.75,317.83,261.78,326.60,320.41]]


def makePlot(actualVals, predictedVals, includeActual = False):
    errors = np.zeros((len(predictedVals),len(predictedVals[0])))
    for j,val in enumerate(actualVals):
        for i in range(len(predictedVals)):
            val2 = predictedVals[i][j]
            errors[i,j] = error(val,val2)
    fig,ax = plt.subplots()
    for j in range(len(predictedVals[0])):
        for i in range(len(predictedVals)):
            if(errors[i,j] >= 40):
                myColor = 'white'
            else:
                myColor = 'black'
            plt.annotate(str(predictedVals[i][j]),(j,i),color=myColor,ha='center',va='center') 
    im = ax.imshow(errors,cmap = 'Reds')
    fig.colorbar(im,orientation = 'vertical')
    plt.xticks(np.arange(0,6),np.arange(1,7))
    if(includeActual):
        plt.yticks(np.arange(0,6),('Actual','SVM','Naive Bayes','Random Forest','R.F. Forced Distance','Neural Net'))
    else:
        plt.yticks(np.arange(0,5),('SVM','Naive Bayes','Random Forest','R.F. Forced Distance','Neural Net'))
    plt.xlabel('Cluster Number')
    plt.title("Expected Scoring\n Shaded by Percent Error")
#    plt.savefig('errorplot.png',bbox_inches = 'tight')
    plt.show()
    
    
makePlot(actualVals,predictedVals,True)