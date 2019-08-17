'''
Created on Jul 2, 2019

@author: anshul
'''

import pandas as pd
import math
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt

class Possession:
    def __init__(self):
        self.passes = 0
        self.ball_distance = 0
        self.passes_into_paint = 0
        self.svm_probability = 0
        self.nn_probability = 0
        self.turnover = 0
        self.foul = 0

class Coordinate:
    def __init__(self, x, y):
        self.x = x 
        self.y = y 

def in_paint(coord):
    if( (19 <= coord.x <= 31) and  ((0 <= coord.y <= 19) or (75 <= coord.y <= 94))):
        return True
    return False
        
def get_sides():
    sideDict = {}
    df = pd.read_csv("data/all_games.csv")
    df.columns = df.columns.str.replace('.', '_')
    half = 1
    for row in df.itertuples():
        if row.home == 'yes' and row.event_id == 3 and row.half == half:
            half += 1
            if row.game_id not in sideDict:
                sideDict[row.game_id] = []
            duke_location = [Coordinate(row.p1_x, row.p1_y), Coordinate(row.p2_x, row.p2_y), Coordinate(row.p3_x, row.p3_y), Coordinate(row.p4_x, row.p4_y), Coordinate(row.p5_x, row.p5_y)]
            opponent_location = [Coordinate(row.p6_x, row.p6_y), Coordinate(row.p7_x, row.p7_y), Coordinate(row.p8_x, row.p8_y), Coordinate(row.p9_x, row.p9_y), Coordinate(row.p10_x, row.p10_y)]
            allLocations = duke_location + opponent_location
            y_coords = [coord.y for coord in allLocations]
            if(all(x > 47 for x in y_coords)):
                sideDict[row.game_id].append("above")
            else:
                sideDict[row.game_id].append("below")
            if len(sideDict[row.game_id]) == 2:
                half = 1
    sideDict[20141126][0] = 'above'
    return(sideDict)

def get_shot_probabilities(shooterID, gameID, x_val):
    shot_df = pd.read_csv("data/shot_chart_compare.csv")
    row = shot_df.loc[(shot_df['shooter'] == shooterID) & (shot_df['game'] == gameID) & (round(shot_df['x'], 2) == round(x_val, 2))].values
    #shot_probs = row.NN_probability.to, row.SVM_probability
    return(row[0][6], row[0][7])
        #df.loc[(df['age'] == 21) & df['favorite_color'].isin(array)]

        
def create_table():
    sideDict = get_sides()
    df = pd.read_csv("data/all_games.csv")
    df.columns = df.columns.str.replace('.', '_')
    in_possession = False
    possession_lst = []
    for row in df.itertuples():
        if row.game_id not in [20150125, 20150117] and row.home == 'yes':
            half = row.half
            gameID = row.game_id
            side = sideDict[gameID][half-1]
            if ((row.ball_y > 47 and side == 'above') or (row.ball_y < 47 and side == 'below')) and not in_possession:
                in_possession = True
                poss = Possession()
                ball = Coordinate(row.ball_x, row.ball_y)
                continue
            if in_possession:
                if row.event_id == 21:
                    poss.ball_distance += math.sqrt((row.ball_x - ball.x)**2 + (row.ball_y - ball.y)**2)
                if row.event_id == 22:
                    poss.ball_distance += math.sqrt((row.ball_x - ball.x)**2 + (row.ball_y - ball.y)**2)
                    poss.passes += 1
                if row.event_id == 23 and in_paint(Coordinate(row.ball_x, row.ball_y)):
                    poss.ball_distance += math.sqrt((row.ball_x - ball.x)**2 + (row.ball_y - ball.y)**2)
                    poss.passes_into_paint += 1
                if row.event_id in [3, 4]:
                    duke_players = [row.p1_global_id, row.p2_global_id, row.p3_global_id, row.p4_global_id, row.p5_global_id]
                    duke_location = [Coordinate(row.p1_x, row.p1_y), Coordinate(row.p2_x, row.p2_y), Coordinate(row.p3_x, row.p3_y), Coordinate(row.p4_x, row.p4_y), Coordinate(row.p5_x, row.p5_y)]
                    poss.nn_probability, poss.svm_probability = get_shot_probabilities(duke_players[row.p_poss - 1], row.game_id, duke_location[row.p_poss - 1].x)
                    possession_lst.append(poss)
                    poss = None
                    in_possession = False
            if in_possession and row.event_id in [7, 8]:
                if row.event_id == 7:
                    poss.turnover = 1
                if row.event_id == 8:
                    poss.foul = 1
                possession_lst.append(poss)
                poss = None
                in_possession = False
        ball = Coordinate(row.ball_x, row.ball_y)
    return possession_lst
                
        
if __name__ == '__main__':
    possessions = create_table()
    passes = []
    ball_dist = []
    paint = []
    nn_prob = []
    svm = []
    for p in possessions:
        if(p.turnover == 0 and p.foul == 0):
            passes.append(p.passes)
            ball_dist.append(p.ball_distance)
            paint.append(p.passes_into_paint)
            nn_prob.append(p.nn_probability)
            svm.append(p.svm_probability)
    plt.scatter(ball_dist, nn_prob)
    plt.show()
    #print(passes)
    """print(r2_score(passes, nn_prob))
    print(r2_score(ball_dist, nn_prob))
    print(r2_score(paint, nn_prob))
    print(r2_score(passes, svm))
    print(r2_score(ball_dist, svm))
    print(r2_score(paint, svm))"""
    
    
    
    
    