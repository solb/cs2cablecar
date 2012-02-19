from Model.interface import PlayerMove
from playerData import *

"""
Cable Car: Student Computer Player

Author: Adam Oest (amo9149@rit.edu)
Author: Solomon Boucher (slb1566@rit.edu)
Author: Brad Bensch (brb7020@rit.edu)
"""

def init(playerId, numPlayers, startTile, logger, arg = "None"):
    """The engine calls this function at the start of the game in order to:
        -tell you your player id (0 through 5)
        -tell you how many players there are (1 through 6)
        -tell you what your start tile is (a letter a through i)
        -give you an instance of the logger (use logger.write("str") 
            to log a message) (use of this is optional)
        -inform you of an additional argument passed 
            via the config file (use of this is optional)
        
    Parameters:
        playerId - your player id (0-5)
        numPlayers - the number of players in the game (1-6)
        startTile - the letter of your start tile (a-j)
        logger - and instance of the logger object
        arg - an extra argument as specified via the config file (optional)

    You return:
        playerData - your player data, which is any data structure
                     that contains whatever you need to keep track of.
                     Consider this your permanent state.
    """
    
    # Put your data in here.  
    # This will be permanently accessible by you in all functions.
    # It can be an object, list, or dictionary
    playerData = PlayerData(logger, playerId, startTile, numPlayers)

    #Our "constants":
    playerData.POWER_STATION_THRESHOLD=20
    
    #statistics collection:
    playerData.totalKills=0
    playerData.totalHits=0
    playerData.dangerousness=0
    playerData.ourGift=0
    playerData.ourGains=0
    
    return playerData

def move(playerData):  
    """The engine calls this function when it wants you to make a move.
    
    Parameters:
        playerData - your player data, 
            which contains whatever you need to keep track of
        
    You return:
        playerData - your player data, 
            which contains whatever you need to keep track of
        playerMove - your next move
    """
    if playerData.firstTurn():
        options = []
        for track in range(1, 33):
            if not playerData.board.routeIsComplete(track):
                if playerData.trackOwner(track)!=playerData.playerId: #not our track
                    possibleFutures=playerData.possibleTrackExtensions(track, False) #look for edges
                    if possibleFutures: #we came up with an option
                        options+=possibleFutures
                        #if playerData.routeInDanger(track,playerData.playerId):
#                            options+=possibleFutures
        if len(options):
            playerData.board.addTile(playerData.makeTile(playerData.currentTile, options[0][2]), options[0][0], options[0][1])
            return playerData, PlayerMove(playerData.playerId, (options[0][0], options[0][1]), playerData.currentTile, options[0][2])
    
    #TODO end their longer tracks over their shorter ones, instead of just looking at the deltas?
    
    unoccupiedCoordinates=[]
    for row in range(8): #where are the vacancies on the board?
        for column in range(8):
            if not playerData.board.lookupTile(row, column): #there's nothing here
                unoccupiedCoordinates.append((row, column))             
                
    validPlacements = []
    for location in unoccupiedCoordinates: #attempt 2: put wherever it's valid
        for rotation in range(4):
            if playerData.mayMoveIllegally[playerData.playerId] or playerData.board.validPlacement(playerData.makeTile(rotation=rotation), location[0], location[1]):
                validPlacements.append(PotentialMove(playerData,location[0],location[1],rotation))
    
    validPlacements.sort(key=lambda choice: choice.enemyLosses*20+choice.ourLosses*-20+choice.deltaEndangerment*-20+choice.enemyGains*-1+choice.ourGains, reverse=True)
    #print(validPlacements)
    
    playerData.totalKills+=validPlacements[0].enemyLosses
    playerData.totalHits+=validPlacements[0].ourLosses
    if validPlacements[0].deltaEndangerment>0:
        playerData.dangerousness+=1
    playerData.ourGift+=validPlacements[0].enemyGains
    playerData.ourGains+=validPlacements[0].ourGains
    
    playerData.board.addTile(playerData.makeTile(rotation=validPlacements[0].rotation), validPlacements[0].row, validPlacements[0].column)
    return playerData, PlayerMove(playerData.playerId, (validPlacements[0].row, validPlacements[0].column), playerData.currentTile, validPlacements[0].rotation)

def move_info(playerData, playerMove, nextTile):
    """The engine calls this function to notify you of:
        -other players' moves
        -your and other players' next tiles
        
    The function is called with your player's data, as well as the valid move of
    the other player.  Your updated player data should be returned.
    
    Parameters:
        playerData - your player data, 
            which contains whatever you need to keep track of
        playerMove - the move of another player in the game, or None if own move
        nextTile - the next tile for the player specified in playerMove, 
                    or if playerMove is None, then own next tile
                    nextTile can be none if we're on the last move
    You return:
        playerData - your player data, 
            which contains whatever you need to keep track of
    """
    playerData.logger.write("move_info() called")
    
    if not playerMove: #we've just moved; here's our next tile
        playerData.currentTile=nextTile
        playerData.opponentsTiles=['' for _ in range(playerData.numPlayers)] #it's a new round and our opponents will have new tiles
    else: #we're looking at someone else's move
        playerData.board.addTile(playerData.makeTile(playerMove.tileName, playerMove.rotation), playerMove.position[0], playerMove.position[1]) #keep track of this tile's location
        playerData.opponentsTiles[playerMove.playerId]=nextTile #remember this player's next tile
    
    if playerData.numPlayers==1 or (playerMove and playerMove.playerId==(playerData.playerId-1)%playerData.numPlayers): #we're either all alone or we'll be up next
        playerData.updateOurStations() #keep watch on our progress and score
        playerData.updateLegalConstraints()
    
    return playerData

################################# PART ONE FUNCTIONS #######################
# These functions are called by the engine during part 1 to verify your board 
# data structure
# If logging is enabled, the engine will tell you exactly which tests failed
# , if any

def tile_info_at_coordinates(playerData, row, column):
    """The engine calls this function during 
        part 1 to validate your board state.
    
    Parameters:
        playerData - your player data as always
        row - the tile row (0-7)
        column - the tile column (0-7)
    
    You return:
        tileName - the letter of the tile at the given coordinates (a-j), 
            or 'ps' if power station or None if no tile
        tileRotation - the rotation of the tile 
            (0 is north, 1 is east, 2 is south, 3 is west.
            If the tile is a power station, it should be 0.  
            If there is no tile, it should be None.
    """
    
    tile=playerData.board.lookupTile(row, column)
    if tile:
        return tile.getType(), tile.getRotation()
    else:
        return None, None

def route_complete(playerData, carId):
    """The engine calls this function 
        during part 1 to validate your route checking
    
    Parameters:
        playerData - your player data as always
        carId - the id of the car where the route starts (1-32)
        
    You return:
        isComplete - true or false depending on whether or not this car
             connects to another car or power station"""
    
    return playerData.board.routeIsComplete(carId)

def route_score(playerData, carId):
    """The engine calls this function 
        during route 1 to validate your route scoring
    
    Parameters:
        playerData - your player data as always
        carId - the id of the car where the route starts (1-32)
        
    You return:
        score - score is the length of the current route from the carId.
                if it reaches the power station, 
                the score is equal to twice the length.
    """
    
    return playerData.board.calculateTrackScore(carId)

def game_over(playerData, historyFileName = None):
    """The engine calls this function after the game is over 
        (regardless of whether or not you have been kicked out)

    You can use it for testing purposes or anything else you might need to do...
    
    Parameters:
        playerData - your player data as always       
        historyFileName - name of the current history file, 
            or None if not being used 
    """
    print 'Times we screwed our opponent: '+str(playerData.totalKills)
    print 'Times we screwed ourselves: '+str(playerData.totalHits)
    print 'Times we left ourselves open: '+str(playerData.dangerousness)
    print 'Points we scored for our opponent: '+str(playerData.ourGift)
    print 'Points we claimed for ourselves: '+str(playerData.ourGains)
    
    '''playerScores=[0 for _ in range(playerData.numPlayers)]
    for track in range(1, 33):
        owner=playerData.trackOwner(track)
        if owner!=-1:
            playerScores[owner]+=playerData.board.calculateTrackScore(track)
            #print 'track '+str(track)+' is worth '+str(playerData.board.calculateTrackScore(track))+' to player '+str(owner)
    
    winners=[]
    for player in range(len(playerScores)):
        if not len(winners):
            winners=[player]
        else: #at least one element
            if playerScores[player]>playerScores[winners[0]]:
                winners=[player]
            elif playerScores[player]==playerScores[winners[0]]:
                winners.append(player)
        
        print 'Player '+str(player)+': score = '+str(playerScores[player])
    
    if len(winners)==1:
        print 'Player #'+str(winners[0])+' has won.'
    else: #there's been at least a two-way tie
        output='Players #'+str(winners[0])
        for player in range(1, len(winners)):
            output+=', #'+str(winners[player])
        output+=' have won.'
        print output'''
