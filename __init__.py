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
    playerData.POWER_STATION_THRESHOLD=15
    
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
    extensions=[] #our tracks that could be extended: stores [row, column, rotation, deltaScore]
    for track in range(1, 33):
        if not playerData.board.routeIsComplete(track):
            if playerData.trackOwner(track)==playerData.playerId: #our track
                currentScore=playerData.board.calculateTrackScore(track)
                possibleFutures=playerData.possibleTrackExtensions(track, False) #avoid edges
                if possibleFutures: #we came up with an option
                    if playerData.routeInDanger(track): #this track needs defense
                        defenses+=possibleFutures
                    elif playerData.board.calculateTrackScore(track): #it this track has already been started, lengthen it (possibly connecting it to a power station)
                        extensions+=possibleFutures
            else: #someone else's
                if playerData.routeInDanger(track, playerData.playerId): #WE pose a threat
                    #print 'NB: We could harm their track '+str(track)
                    currentScore=playerData.board.calculateTrackScore(track)
                    possibleFutures=playerData.possibleTrackExtensions(track, True) #aim to complete their tracks
                    if possibleFutures: #we came up with an option
                        attacks+=possibleFutures
    defenses.sort(key=lambda inNeed: inNeed[4], reverse=True) #our highest gain first
    attacks.sort(key=lambda wideOpen: wideOpen[4]) #their lowest gain first
    attacks.sort(key=lambda wideOpen: wideOpen[3], reverse=True) #their longest first
    extensions.sort(key=lambda needsWork: needsWork[4], reverse=True) #our highest gain first
    
    print 'NB: Our best defenses are:\n'+str(defenses)
    print 'NB: Our best attacks are:\n'+str(attacks)
    print 'NB: Our best extensions are:\n'+str(extensions)
    
    #observations after watching GoodComputer:
    #TODO if we go first, consider extending their track
    #TODO when extending our tracks (not defending them), consider the longest first
    #TODO random should be used to create additional sinks to the edge
    
    #TODO weigh DEFENSE against OFFENSE
    if len(attacks):
        #print 'NB: Commencing attack run...'
        #print 'I think I\'m going to find this there: '+str(playerData.board.lookupTile(attacks[0][0], attacks[0][1]))
        playerData.board.addTile(playerData.makeTile(playerData.currentTile, attacks[0][2]), attacks[0][0], attacks[0][1])
        return playerData, PlayerMove(playerData.playerId, (attacks[0][0], attacks[0][1]), playerData.currentTile, attacks[0][2])
    elif len(defenses):
        #print 'NB: On guard!'
        playerData.board.addTile(playerData.makeTile(playerData.currentTile, defenses[0][2]), defenses[0][0], defenses[0][1])
        return playerData, PlayerMove(playerData.playerId, (defenses[0][0], defenses[0][1]), playerData.currentTile, defenses[0][2])
    elif len(extensions):
        #print 'NB: Adding onto one of our tracks...'
        playerData.board.addTile(playerData.makeTile(playerData.currentTile, extensions[0][2]), extensions[0][0], extensions[0][1])
        return playerData, PlayerMove(playerData.playerId, (extensions[0][0], extensions[0][1]), playerData.currentTile, extensions[0][2])
    
    #TODO if we can't find a good move to make, extend one of our opponent's tracks, prefereably so that it is vulnerable
    #TODO find each opponent's best-scoring move and block it
    #TODO puppy guard opponents' stations
    #FIXME choose the best-scoring rotation whenever we choose a tile
    #FIXME do a better job of starting out our tracks: if nothing is in danger, don't randomly start any!
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
    print 'NB: Making a random move!'
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
                #print 'NB: Making a legal move.'
                return playerData, PlayerMove(playerData.playerId, (location[0], location[1]), playerData.currentTile, rotation)
    
    playerData.board.addTile(playerData.makeTile(rotation=rotation), unoccupiedCoordinates[0][0], unoccupiedCoordinates[0][1])
    #print 'NB: Making an illegal move!'
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
    playerScores=[0 for _ in range(playerData.numPlayers)]
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
        print output
