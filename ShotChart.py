'''
Created on Jun 25, 2019

@author: anshul
'''
import DataPrep
import numpy as np
from sklearn.preprocessing import scale
import NeuralNet
import pandas as pd
import Gravity

def data():
    ret = {}
    data, info = DataPrep.create_dataframe()
    data_array = scale(np.array(data))
    nn_predicted = NeuralNet.predict(data_array, 10)
    for i in range(len(info)):
        info[i].append(nn_predicted[i][1])
        if info[i][0] not in ret:
            ret[info[i][0]] = {}
        if info[i][1] not in ret[info[i][0]].items():
            ret[info[i][0]][info[i][1]] = nn_predicted[i][1]
    df = pd.DataFrame(info, columns = ["game", "time", "shot_num", "value", "result", "ePPS"])
    df.to_csv("test_gravity_NN.csv")

def add_column():
    shots = Gravity.get_vectors()[1]
    df = pd.read_csv("data/test_gravity_NN.csv")
    final_list = []
    for row in df.itertuples():
        game = row.game
        time = row.time
        if time in shots[game]:
            lst = list(row[2:])
            temp = [[] for i in range(5)]
            grav_dict = shots[game][time][0]
            for j in range(5):
                for k, v in grav_dict.items():
                    if v[j] != 0:
                        temp[j].extend(v[j])
            avgs = [sum(temp[i])/len(temp[i]) if len(temp[i]) > 0 else 0 for i in range(5)]
            lst.extend(avgs)
            lst.extend(shots[game][time][1])
            final_list.append(lst)
    #print(final_list)
    ret = pd.DataFrame(final_list, columns = ["game", "time", "shot_number", "value", "result", "probability", "avg_one", "avg_two", "avg_three", "avg_four", "avg_five", "p1", "p2", "p3", "p4", "p5"])
    pps = ret.value * ret.result
    epps = ret.value * ret.probability
    ret['epps'] = epps
    ret['pps'] = pps
    ret = ret.drop(columns = ['result'])
    ret.to_csv("gravity_with_players_changed_zones.csv")
    print(ret)
            
if __name__ == '__main__':
    #data()
    add_column()
