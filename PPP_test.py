'''
Created on Jun 21, 2019

@author: anshul
'''
import pandas as pd
import SVM
import NaiveBayes
import NeuralNet
import PCA
import pandas as pd
import numpy as np
#Test Naive Bayes, SVM

class Shot:
    def __init__(self, player):
        self.shooter = player
        self.gameID = 0
        self.distance_ten_seconds = 0 #DONE
        self.distance_total_game = 0 #DONE
        self.velocity = 0 #DONE
        self.distance_closest_def = 0 #DONE
        self.angle_closest_def = 0  #DONE
        self.distance_second_def = 0
        self.angle_second_def = 0
        self.shot_distance = 0 #DONE
        self.shot_angle = 0 #DONE
        self.angle_closest_teammate = 0 #DONE
        self.distance_closest_teammate = 0 #DONE
        self.offense_convex_hull = 0
        self.defense_convex_hull = 0
        self.shot_clock = 0
        self.second_chance = 0
        self.catch_and_shoot = 0 #DONE
        self.result = 0 #DONE
        self.value = 0
        
def getShots():
    shotDict = {}
    df = pd.read_csv("data/shots_standardized.csv")
    for row in df.itertuples():
        if row.cluster not in shotDict:
            shotDict[row.cluster] = []
        myShot = Shot(row.shooterID)
        myShot.distance_ten_seconds = row.distance_ten_seconds
        myShot.distance_total_game = row.distance_game
        myShot.velocity = row.velocity
        myShot.distance_closest_def = row.distance_closest_def
        myShot.angle_closest_def = row.angle_closest_def
        myShot.distance_second_def = row.distance_second_def
        myShot.angle_second_def = row.angle_second_def
        myShot.shot_distance = row.shot_dist
        myShot.shot_angle = row.shot_angle
        myShot.distance_closest_teammate = row.distance_closest_teammate
        myShot.angle_closest_teammate = row.angle_closest_teammate
        myShot.offense_hull = row.offense_hull
        myShot.defense_hull = row.defense_hull
        myShot.shot_clock = row.shot_clock
        myShot.catch_and_shoot = row.catch_shoot
        myShot.result = row.result
        myShot.value = row.value
        shotDict[row.cluster].append(myShot)
    return shotDict

def train(model, clusterNum, components):
    d = getShots()
    data = []
    results = []
    values = []
    scored = 0
    expected = 0
    for shot in d[clusterNum]:
        data.append([shot.distance_ten_seconds, shot.distance_total_game, shot.velocity , shot.distance_closest_def, shot.angle_closest_def, 
                    shot.distance_second_def,shot.angle_second_def,  shot.angle_closest_teammate, shot.distance_closest_teammate, shot.shot_distance, 
                    shot.shot_angle, shot.offense_hull, shot.defense_hull, shot.shot_clock, shot.catch_and_shoot])
        results.append(shot.result)
        values.append(shot.value)
    if model == "SVM":
        prob = SVM.predict(data, components)[0]
        shot_prob = [each[1] for each in prob]
    if model == "NaiveBayes":
        prob = NaiveBayes.predict(data, components)[0]
        shot_prob = [each[1] for each in prob]
    if model == "NeuralNet":
        prob = NeuralNet.predict(data, components)
        shot_prob = [each[1] for each in prob]
    print(shot_prob)
    print(len(shot_prob))
    for i in range(len(data)):
        value = values[i]
        if results[i] == 1:
            scored += value
        expected += (shot_prob[i]* value)
    #print(count/total)
    print("Expected points:", str(expected), "Actual points:", str(scored))
    return(expected)
    
if __name__ == '__main__':
    
    for i in range(1,7):
        train("NeuralNet", i, 10)

