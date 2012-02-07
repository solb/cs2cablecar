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

    # This is how you write data to the log file
    playerData.logger.write("Player %s starting up" % playerId)
    
    # This is how you print out your data to standard output (not logged)
    print(playerData)
    
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
    #TODO we currently don't count PowerStation connections as completions at all; should we?
    defenses=[] #our tracks in need of saving: stores [row, column, rotation, deltaScore]
    attacks=[] #opponents' vulnerable tracks: stores [row, column, rotation, deltaScore]
    for track in range(1, 33):
        if not playerData.board.routeIsComplete(track):
            if playerData.trackOwner(track)==playerData.playerId: #our track
                if playerData.routeInDanger(track):
                    currentScore=playerData.board.calculateTrackScore(track)
                    possibleFutures=playerData.possibleTrackExtensions(track, False) #avoid completing our tracks
                    for option in possibleFutures:
                        option[3]-=currentScore #only consider our gain, not the total track score
                        defenses.append(option)
            else: #someone else's
                if playerData.routeInDanger(track, playerData.playerId): #WE pose a threat
                    currentScore=playerData.board.calculateTrackScore(track)
                    possibleFutures=playerData.possibleTrackExtensions(track, True) #aim to complete their tracks
                    
                    for option in possibleFutures:
                        option[3]-=currentScore #only consider their gain, not the total track score
                        attacks.append(option) #TODO Should we be able to take out our anger on specific players?
    defenses.sort(key=lambda inNeed: inNeed[3], reverse=True) #our highest current score first
    attacks.sort(key=lambda wideOpen: wideOpen[3]) #their lowest gain first
    
    print 'NB: Our best defenses are:\n'+str(defenses)
    print 'NB: Our best attacks are:\n'+str(attacks)
    
    if len(defenses):
        print 'NB: On guard!'
        playerData.board.addTile(playerData.makeTile(playerData.currentTile, defenses[0][2]), defenses[0][0], defenses[0][1])
        return playerData, PlayerMove(playerData.playerId, (defenses[0][0], defenses[0][1]), playerData.currentTile, defenses[0][2])
    elif len(attacks):
        print 'NB: Commencing attack run...'
        print 'I think I\'m going to find this there: '+str(playerData.board.lookupTile(attacks[0][0], attacks[0][1]))
        playerData.board.addTile(playerData.makeTile(playerData.currentTile, attacks[0][2]), attacks[0][0], attacks[0][1])
        return playerData, PlayerMove(playerData.playerId, (attacks[0][0], attacks[0][1]), playerData.currentTile, attacks[0][2])
    
    
    
    #FIXME weigh DEFENSE against OFFENSE
    #FIXME choose the best-scoring rotation whenever we choose a tile
    #FIXME do a better job of starting out our tracks
    #FIXME end their longer tracks over their shorter ones, instead of just looking at the deltas?
    
    
    #code for optimized choice of route to extend:
    '''currentScore=playerData.board.calculateTrackScore(track)
                    row, column=playerData.board.lookupTileCoordinates(playerData.board.followRoute(track)[0])
                    for rotation in range(4):
                        ourTile=playerData.makeTile(rotation=rotation)
                        playerData.board.addTile(ourTile, row, column)
                        
                        playerData.board.removeTile(ourTile, row, column)'''
    
    #END GOOD CODE!
    
    #give up: put it wherever it's valid #TODO make this smarter/absent, or at least more efficient
    unoccupiedCoordinates=[]
    for row in range(8): #where are the vacancies on the board?
        for column in range(8):
            if not playerData.board.lookupTile(row, column): #there's nothing here
                unoccupiedCoordinates.append((row, column))
    for location in unoccupiedCoordinates: #attempt 2: put wherever it's valid
        for rotation in range(4):
            tile=playerData.makeTile(rotation=rotation)
            if playerData.board.validPlacement(tile, location[0], location[1]):
                playerData.board.addTile(tile, location[0], location[1])
                print 'Making a legal move.'
                return playerData, PlayerMove(playerData.playerId, (location[0], location[1]), playerData.currentTile, rotation)
    
    playerData.board.addTile(playerData.makeTile(), unoccupiedCoordinates[0][0], unoccupiedCoordinates[0][1], rotation)
    print 'Making an illegal move!'
    return playerData, PlayerMove(playerData.playerId, (unoccupiedCoordinates[0][0], unoccupiedCoordinates[0][1]), playerData.currentTile, rotation) #final attempt: stick it somewhere it shouldn't be

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
    
    # Test things here, changing the function calls...
    print "History File: %s" % historyFileName
    print "If it says False below, you are doing something wrong"
    
    if historyFileName == "example_complete_start.data":
        print tile_info_at_coordinates(playerData, 5, 2) == ('e', 0)
        print tile_info_at_coordinates(playerData, 2, 1) == ('j', 0)
        print tile_info_at_coordinates(playerData, 1, 2) == ('b', 0)
        #print route_complete(playerData, 1) == True
        #print route_score(playerData, 1) == 3
    elif historyFileName == "example_complete.data":
        print tile_info_at_coordinates(playerData, 5, 5) == ('e', 1)
        print tile_info_at_coordinates(playerData, 1, 0) == ('a', 0)
        print tile_info_at_coordinates(playerData, 3, 3) == ('ps', 0)
    elif historyFileName == "example_incomplete1.data":
        print route_complete(playerData, 29) == False
        print route_complete(playerData, 5) == False
        print route_complete(playerData, 11) == False
        print route_score(playerData, 22) == 0
        print route_score(playerData, 26) == 1
        print route_score(playerData, 18) == 1
    elif historyFileName == "example_incomplete2.data":
        print route_complete(playerData, 8) == False
        print route_complete(playerData, 25) == True
        print route_complete(playerData, 22) == False
        print route_score(playerData, 20) == 2
        print route_score(playerData, 26) == 3
        print route_score(playerData, 21) == 3
    elif historyFileName == "slb1566-1a.data":
        print tile_info_at_coordinates(playerData, 4, 0) == ('b', 1)
        print tile_info_at_coordinates(playerData, 6, 1) == ('d', 1)
        print tile_info_at_coordinates(playerData, 0, 4) == ('a', 1)
        print route_complete(playerData, 21) == True
        print route_complete(playerData, 1) == True
        print route_complete(playerData, 11) == True
        print route_score(playerData, 10) == 2
        print route_score(playerData, 24) == 4
        print route_score(playerData, 20) == 54
