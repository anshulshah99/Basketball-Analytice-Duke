'''
Created on Jul 23, 2019

@author: anshul
'''
import pandas as pd
import math as m
import BarycentricPairing
import TriangleInterpolation
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def check_halfcourt(y_coords, side):
    if side == "above":
        return(all(x > 47 for x in y_coords))
    else:
        return(all(x < 47 for x in y_coords))

def distance(coord_1, coord_2):
    #calculate distance between two points
    dist = m.sqrt((coord_1.x - coord_2.x)**2 + (coord_1.y - coord_2.y)**2)
    return dist

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
            y_coords = [coord.y for coord in duke_location]
            if(all(y > 47 for y in y_coords)):
                sideDict[row.game_id].append("above")
            else:
                sideDict[row.game_id].append("below")
            if len(sideDict[row.game_id]) == 2:
                half = 1
    sideDict[20141126][0] = 'above'
    return(sideDict)

def process(gravity_dicts):
    playerDict = {}
    for i in range(len(gravity_dicts) - 1):
        d = gravity_dicts[i]
        for k, v in d.items():
            if k != 'time' and k != 'ball_handler':
                if k not in playerDict:
                    playerDict[k] = [[] for i in range(10)]
                scores = [val for val in v if val != "N/A"]
                if len(scores) > 0:
                    playerDict[k][i] = scores
    ball_gravity = gravity_dicts[-1]
    for j in range(len(ball_gravity['time'])):
        player = ball_gravity['player'][j]
        ind = ball_gravity['zone'][j] + 4
        grav = ball_gravity['gravity'][j]
        playerDict[player][ind].append(grav)
    return playerDict

def analyze(playerID):
    playerDict = {}
    possession = False
    offReb = False
    sideDict = get_sides()
    df = pd.read_csv("data/all_games.csv")
    df.columns = df.columns.str.replace('.', '_')
    for row in df.itertuples():
        if row.game_id in [20141114, 20150320, 20141122, 20141126, 20150103, 20150218]:
            half = row.half
            time = round(row.game_clock + (1200 * (2 - half)), 2)
            gameID = row.game_id
            side = sideDict[gameID][half-1]
            duke_players = [row.p1_global_id, row.p2_global_id, row.p3_global_id, row.p4_global_id, row.p5_global_id]
            duke_location = [Coordinate(row.p1_x, row.p1_y), Coordinate(row.p2_x, row.p2_y), Coordinate(row.p3_x, row.p3_y), Coordinate(row.p4_x, row.p4_y), Coordinate(row.p5_x, row.p5_y)]
            opponent_location = [Coordinate(row.p6_x, row.p6_y), Coordinate(row.p7_x, row.p7_y), Coordinate(row.p8_x, row.p8_y), Coordinate(row.p9_x, row.p9_y), Coordinate(row.p10_x, row.p10_y)]
            y_coords = [coord.y for coord in duke_location]
            ball = Coordinate(row.ball_x, row.ball_y)
            if row.event_id == 5 and row.home == 'yes':
                offReb = True
            if gameID not in playerDict:
                playerDict[gameID] = ([],[], [])
            if row.event_id == 8 and not possession:
                continue
            if check_halfcourt(y_coords, side) and row.home == 'yes' and not possession and not offReb and row.event_id not in [1, 2, 8, 11, 28] and playerID in duke_players:
                #offReb = False
                possession = True
                possDict = {}
                if side == 'above':
                    hoop = Coordinate(25, 88.75)
                if side == 'below':
                    hoop = Coordinate(25, 5.25)
                if time not in possDict:
                    possDict[time] = {}
            if offReb and row.home == "no":
                offReb = False
            if playerID not in duke_players:
                possession = False
                possDict = {}
                continue
            if possession:
                if row.home == 'yes':
                    ball_handler = duke_players[row.p_poss - 1]
                
                if row.event_id in [1, 2]:
                    continue
                
                if row.event_id == 8 and row.home == 'no':
                    possession = False
                    continue
                
                if row.event_id == 3 or row.event_id == 4:
                    
                    if time not in possDict:
                        possDict[time] = {}
                    pairs = BarycentricPairing.newPairing(duke_location, opponent_location)
                    for d, o in pairs:
                        possDict[time][duke_players[o]] = [opponent_location[d], duke_location[o], ball, hoop]
                    possDict[time][ball_handler].append(0)
                    one, two, three, four, five, ball_gravity = TriangleInterpolation.find_average(possDict)
                    final_dict = process([one, two, three, four, five, ball_gravity])
                    offball_five = final_dict[playerID][4]
                    onball_five = final_dict[playerID][9]
                    if len(offball_five) > 0:
                        playerDict[gameID][0].append(sum(offball_five)/len(offball_five))
                    else:
                        playerDict[gameID][0].append(1)
                    if len(onball_five) > 0:
                        playerDict[gameID][1].append(sum(onball_five)/len(onball_five))
                    else:
                        playerDict[gameID][1].append(1)
                    if row.global_player_id == playerID:
                        playerDict[gameID][2].append(1)
                    else:
                        playerDict[gameID][2].append(0)
                    possession = False
                    continue
                
                if row.event_id == 5:
                    
                    """gravityDict = TriangleInterpolation.find_average(possDict)
                    playerDict[gameID][0].append(sum(gravityDict[playerID])/len(gravityDict[playerID]))
                    playerDict[gameID][1].append(0)"""
                    offReb = True
                    possession = False
                    continue
                
                if row.event_id == 6:
                    possession = False
                    continue
                
                if row.event_id == 7:
                    """if time not in possDict:
                        possDict[time] = {}
                    pairs = BarycentricPairing.newPairing(duke_location, opponent_location)
                    for d, o in pairs:
                        possDict[time][duke_players[o]] = [opponent_location[d], duke_location[o], ball, hoop]
                    possDict[time][ball_handler].append(0)
                    one, two, three, four, five, ball_gravity = TriangleInterpolation.find_average(possDict)
                    final_dict = process([one, two, three, four, five, ball_gravity])
                    playerDict[gameID].append(final_dict)"""
                    possession = False
                    continue
        
                if row.event_id == 15:
                    possDict = {}
                    possession = False
                    continue
                
                
                if row.event_id == 28 or row.event_id == 11:
                    continue
                if time not in possDict:
                    possDict[time] = {}
                ball = Coordinate(row.ball_x, row.ball_y)
                pairs = BarycentricPairing.newPairing(duke_location, opponent_location)
                for d, o in pairs:
                    possDict[time][duke_players[o]] = [opponent_location[d], duke_location[o], ball, hoop]
                possDict[time][ball_handler].append(0)
    return playerDict
            

if __name__ == '__main__':
    d = analyze(601140)
    fig = plt.figure()
    i = 0
    for k, v in list(d.items()):
        i+= 1
        lst = []
        count = 0
        for num in v[2]:
            if num == 1:
                count += 1
            lst.append(count)
        ax = plt.subplot(3, 2, i)
        ax.scatter(range(len(v[0])),v[0],color='r')
        r2, pval = pearsonr(lst, v[0])
        print(r2)
        ax.set_title(k)
        ax.set_xlim(0,len(v[0])-1)
        ax.set_xticks(range(len(v[0])))
        ax.set_xticklabels(lst)
    plt.show()