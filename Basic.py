import pandas as pd
import math as m
import scipy.spatial as sp
import numpy as np
import matplotlib.pyplot as plt

# X and Y dimensions for a basketball court
UPPER_X_LIM = 94
UPPER_Y_LIM = 50

#  Each Coordinate object contains a position for a single entity at a moment 
#  during the game. Setting ERROR_WHEN_OUT to true will make coordinates outside 
#  the court boundaries invalid, and an Error will be thrown if one attempts to 
#  initialize them

class Coordinate:
    def __init__(self, x, y, z=0, ERROR_WHEN_OUT=False):
        if(ERROR_WHEN_OUT):
            if(Coordinate.isOut(x,y)):
                raise ValueError('Invalid Position on Court')
        self.x=x
        self.y=y
        self.z=z
        return

# Basic function for finding Euclidean distance in 2D space
def distanceTo(coord_1, coord_2):
    dist=m.sqrt((coord_1.x - coord_2.x)**2 + (coord_1.y - coord_2.y)**2)
    return dist

# If a player is outside the rectangular boundaries of the court, this function
# returns true. 
def isOut(x,y):
    if(((x < 0) or (y < 0)) or ((x > UPPER_X_LIM) or (y > UPPER_Y_LIM))):
        return True
    else:
        return False
                
# This class defines Players, whose main attribute is a a dictionary (positions)
# with timestamps as keys and Coordinate objects as values. There are also 
# methods for determining useful player statistics, such as distance traveled
# and speed.
class Player:
    # The time increment in SportVU Data is .04s, which is common to all players
    myTimeIncrement = .04
    # In the case of no name being provided, the name is unknown + the player's ID.
    # Unlike a name, a player ID is required to manipulate the SportVU Data
    def __init__(self, playerID, playerName = 'unknown'):
        # Name must be a string
        if(not isinstance(playerName, str)):
            raise TypeError('Invalid player name')
        if(playerName == 'unknown'):
            playerName = playerName + str(playerID)
        # Initializes the player name and ID (both of which are immutable)
        # and creates an empty dictionary for positions
        self.name=playerName
        self.id=playerID
        self.positions = {}
        return
    
    # This method adds a player's Coordinate object at a given moment t to the
    # position dictionary. 
    def addPosition(self, playerCoord, t):
        self.positions.update({t : playerCoord})
        return
    
    # This method returns the current position dictionary. The same data 
    # could also be accessed through Player.positions
    def getPositionDict(self):
        return self.positions
    
    # Returns the total distance traveled during a game by summing segments of
    # Euclidean distance from moment to moment, for all times the player is in.
    def getGameDistance(self):
        gameDist=0
        for t in self.positions.keys():
                        if(not isOut(self.positions.get(t)) and (t + self.myTimeIncrement) in self.positions.keys()):
                                gameDist=gameDist + distanceTo(self.positions.get(t), self.positions.get(t + self.myTimeIncrement))
                        else: continue
        return gameDist
    
    # Finds speed between 2 times t1 and t2, assuming velocity is constant
    # If t1 is not provided as an argument, it defaults to calculating instantaneous velocity
    def findSpeed(self, t2, t1 = None):
        
        if(t1 == None):
            t1 = t2 - self.myTimeIncrement
        dist=distanceTo(self.positions.get(t1),self.positions.get(t2))
        time=t2-t1
        return dist / time
    
    # Finds acceleration between 2 times t1 and t2, assuming acceleration is near-constant
    # If t1 is not provided as an argument, it defaults to calculating instantaneous acceleration
    def findAcceleration(self, t2, t1 = None):
        if(t1 == None):
            t1 = t2 - self.myTimeIncrement
        speed1 = self.findSpeed(t1,t1 + self.myTimeIncrement)
        speed2 = self.findSpeed(t2,t2 + self.myTimeIncrement)
        accel = (speed2 - speed1)/(t2-t1)
        return accel
    
    # Iterates through the list of possible defenders and calculates the Euclidean
    # distance between the defender and self. If one (or more) defenders are
    # within a distance given by "radius," returns True.
    def isGuarded(self, t, defenders, radius = 5):
                for p in defenders:
                        if(distanceTo(self.positions.get(t),p.positions.get(t)) > radius):
                                return True
                return False

# Make empty list for Player IDs which have already been encountered
playerIDList = []

# Make empty dictionaries with Player IDs as keys and Player objects as values
# for both teams
homeTeam = {}
awayTeam = {}

# Make empty dictionary with timestamps as keys and the entity with possession 
# as values. 
possessionTracker = {}


# Reads in CSV formatted file of SportVU data
def initialize(filename = "mydata.csv"):
        df = pd.read_csv(filename)
        # Iterate over each row in data
        for row in df.itertuples():
                gameClock = row.game_clock
                quarter = row.quarter
                # The adjustedClock variable makes it possible to timestamp games
                # as if there were a single clock counting down from 2880 seconds
                # as opposed to a 720s clock that resets 4 times.
                adjustedClock = 2880 - quarter * 720 + gameClock
                # The possessing team and player at any given moment are stored 
                # in a tuple so that most relevant possession data is stored in one place
                playerWithPossession = row.ent_w_poss
                teamWithPossession = row.team_w_poss
                possTuple = (playerWithPossession, teamWithPossession)
                possessionTracker.update({adjustedClock:possTuple})
                # Loop over each team then over each player, collecting Player
                # ID and x and y coordinates.
                for letter in "ah":
                        for num in range(1,6):
                            
                                # lDict and globals() have to be used to make the
                                # exec statements work properly (and avoid having 30+ lines of code
                                # doing the same thing as these 7 lines)
                                lDict = locals()               
                                exec('ID = row.' + letter + str(num) + '_ent',globals(),lDict)
                                ID = lDict['ID']
                                exec('x = row.' + letter + str(num) + '_x',globals(),lDict)
                                x = lDict['x']
                                exec('y = row.' + letter + str(num) + '_y',globals(),lDict)
                                y = lDict['y']
                                
                                # Two data points in myData.csv are listed as NA,
                                # leading to NAN player IDs. This skips over 
                                # saving these NAN IDs.
                                if(np.isnan(ID)):
                                        continue
                                    
                                # Casts IDs as integers in case they got read in
                                # as floats
                                if(isinstance(ID,float)):
                                    ID = int(ID)
                                
                                # When a previously unencountered PlayerID is found,
                                # create a new Player object for it and store it in 
                                # the list of known players
                                if(ID not in playerIDList):
                                        # Put name in here
                                        newPlayer = Player(ID)
                                        playerIDList.append(ID)
                                        if(letter == 'a'):
                                                awayTeam.update({ID : newPlayer})
                                        else:
                                                homeTeam.update({ID : newPlayer})
                                                
                                # Add a new Coordinate object to the current Player's
                                # positions 
                                coord = Coordinate(x,y)
                                if(letter == 'a'):
                                        awayTeam.get(ID).addPosition(coord, adjustedClock)
                                elif(letter == 'h'):
                                        homeTeam.get(ID).addPosition(coord, adjustedClock)

# If a time of interest is in between two SportVU data points, this function floors
# that time to the nearest acceptable point                                       
def nearTime(time):
    if(time < 0 or time > 2880):
        raise ValueError('Invalid time input')
    timeConv = time / Player.myTimeIncrement
    timeFlo = m.floor(timeConv)
    near = timeFlo * Player.myTimeIncrement
    return near

# Whenever an operation relies on accessing SportVU data, it should call on
# initializeCheck to ensure the data has been read in and will not throw and Attribute Error
def initializeCheck():
    if(len(awayTeam) == 0):
        initialized = False
        whatDo = input("Data is not yet initialized. Initialize now? (Y/N)\n")
        if(whatDo == 'Y'):
            initialize()
            initialized = True
        else:
            print("The operation you attempted will not take place because there is no data yet")
    else:
        initialized = True
    return initialized

# Converts the "adjustedClock" format (counting down from 2880 seconds in a game)
# into a more familiar quarters / seconds format.            
def adjustedClockParser(adjustedClock):
    quarter = int(5 - adjustedClock / 720)
    time = adjustedClock % 720
    print('quarter: ' + str(quarter) + '\ntime: ' + str(time))
    
def convexHull(players, plot = False):
    initializeCheck()
    xLocs = []
    yLocs = []
    for i in players:
        xLocs.add[i.x]
        yLocs.add[i.y]
    hullArray = np.array(xLocs,yLocs)
    hull = sp.ConvexHull(hullArray)
    if(plot == True):
        for simplex in hull.simplices:
            plt.plot(xLocs[simplex], yLocs[simplex], 'k-')
    return hull

def getArea(hull):
    return hull.Area


def avgTeamSpeed(team, t1, t2):
    initializeCheck()
    teamSum = 0
    teamCount = 0
    for p in team.values():
        teamSum = teamSum + p.findSpeed(t1, t2)
        teamCount = teamCount + 1
    return teamSum / teamCount

def isFastBreak(possID, fastBreakWindow = 8, areaThreshold = 1.4, speedThreshold = 1.2, verbose = False):
        initializeCheck()
        playTooLong = False
        playInterrupted = False
        offenseSpreadOut = False
        offenseFast = False

        # We'll need some way to figure out times corresponding to possession IDs
        if(endTime(possID) - startTime(possID) > fastBreakWindow):
                playTooLong = True
        elif(shotclockTimeElapsed != universalTimeElapsed):
                playInterrupted = True
        else:
                offenseHull = convexHull(offense)
                offenseArea = getArea(offenseHull)
                defenseHull = convexHull(defense)
                defenseArea = getArea(defenseHull)

                if(offenseArea > (areaThreshold * defenseArea)):
                        offenseSpreadOut = True
                if(avgTeamSpeed(offense) > (speedThreshold * avgTeamSpeed(defense))):
                        offenseFast = True
                if(verbose):
                        if(not playInterrupted and not playTooLong):
                                if(offenseSpreadOut and offenseFast):
                                        return('All conditions met for fast break using current Thresholds')
                                elif(offenseSpreadOut):
                                        return('Offense is spread out but not moving significantly faster than defense')
                                elif(offenseFast):
                                        return('Offense is moving quickly but not covering significantly more court than defense')
                                else:
                                        return('Play is uninterrupted and short but offense is neither faster nor more spread out than defense')
                        else:
                                if(playInterrupted):
                                        return('Play was interrupted and so cannot be considered a fast break')
                                if(playTooLong):
                                        return('Play was too long under current window (default = 8s) to be considered a fast break')
                else:
                        if(not playInterrupted and not playTooLong and offenseSpreadOut and offenseFast):
                                return True
                        else:
                                return False

def angleWRTBasket(coord):
        NET_COORDINATES = (25,4)
        deltaX = coord.x - NET_COORDINATES[0]
        deltaY = coord.y - NET_COORDINATES[1]
        return m.degrees(m.atan(deltaY / deltaX))






                
                   

#def minutesPlayed(player, start=0, end=-1)
#def pointsPerMin(shots, player, start=0, end=-1)

#def howHotShots(shots, times, startHot, endHot, player):
## Takes a list of shots taken and timestamps for these shots, along with indices for the "Hot" period in question
## Determines whether the past [endHot-startHot] shots by [player] showed a higher point-scoring ability than the preceding game
## Returns a string detailing whether the past [endHot-startHot] shots were
## better, and if so how much
#
#    # Making sure arguments are valid
#    if(startHot < 0 or endHot < 0):
#        raise Error('Starting and ending indices must be non-negative')
#    elif(startHot >= endHot):
#        raise Error(
#            'Starting index cannot be greater than or equal to ending index')
#
#
#    # Calculate sum of points during "Hot" period
#    sumShots=0
#    for i in range(startHot, endHot + 1):
#        sumShots=shots[i] + sumShots
#
#    # Calculate duration of time during "Hot" period
#    duration=times[startHot] - times[endHot]
#
#    # Determine the rate at which the player scores points during hot period
#    hotRate=sumShots / duration
#    return (hotRate / (pointspermin(shots, player, 0, startHot) - 1) * 100)
    # Return string describing results
# if(hotRate < pointspermin(shots, player, 0, startHot)):
# return("Player is not scoring better than their previous average")
# else
# x = (hotRate/pointspermin(shots, player, 0, startHot) - 1) * 100
# return("Player is scoring " + x + "% more than before")


# def howHotTime(shots
# Determines the rate of scoring in the past [interval] minutes as opposed
# to the past N plays in the "Shots" hotness function

#def hotAfterTimeout(shots, times, player, timeoutIndex, interval = 4):
## Determines the difference in [player]'s shooting before and after a timeout takes place. If negative, the player was shooting better after the timeout
## than before it. If positive, they "cooled down," during the timeout.
## Returns the difference in shooting as a percentage value
#        ret=howHotShots(shots,
#    times,
#    player,
#    timeoutIndex - interval,
#    timeoutIndex) - howHotShots(shots,
#    times,
#    player,
#    timeoutIndex,
#     timeoutIndex + interval)
#        return ret
