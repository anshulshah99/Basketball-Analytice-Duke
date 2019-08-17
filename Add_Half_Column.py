'''
Created on Jun 16, 2019

@author: anshul
'''
import pandas as pd
 
def read_csv(filename):
    df = pd.read_csv(filename)
    df.columns = df.columns.str.replace('.', '_')
    return df
 
def compute_percentage(df):
    col=[]
    half = 0
    gameID = 0
    for row in df.itertuples():
        if row.game_clock == 1200 and half == 1:
            half = 2
        if row.game_id != gameID:
            gameID = row.game_id
            half = 1
        col.append(half)
    return col

if __name__ == '__main__':
    df = read_csv('data/games_1415.csv')
    computed_values = compute_percentage(df)
    df['half'] = computed_values
    df.to_csv('all_games.csv')