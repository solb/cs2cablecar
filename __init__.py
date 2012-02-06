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
    #FIXME re-implement this whole thing functionally
    #FIXME weigh DEFENSE against OFFENSE
    #FIXME choose the best-scoring rotation whenever we choose a tile
    
    playerData.logger.write("move() called")
    #TODO do a better job of starting our tracks safely
    
    #defend our tracks: save those that are in danger
    #TODO defend more than just the first such problem we see
    #TODO look after our unstarted routes, too
    for station in range(1, 33):
        if playerData.trackOwner(station)==playerData.playerId and not playerData.board.routeIsComplete(station) and playerData.board.calculateTrackScore(station): #this is ours, has been started, and is unfinished
            endOfLine=playerData.board.followRoute(station)
            row, column=playerData.board.lookupTileCoordinates(endOfLine[0])
            routeSide=endOfLine[1]
            for threat in playerData.opponentsTiles: #we're going to make sure no opponent could shut this down
                trackAtRisk=False
                for newRotation in range(4):
                    threateningTile=playerData.makeTile(threat, newRotation)
                    if not playerData.board.lookupTile(row, column): #nothing here yet
                        playerData.board.addTile(threateningTile, row, column, False) #populate this with the board's knowledge
                        if threateningTile.routeComplete(routeSide): #we could be thwarted
                            trackAtRisk=True
                            break
                if trackAtRisk:
                    for rotation in range(4):
                        tile=playerData.makeTile(rotation=rotation)
                        if playerData.board.validPlacement(tile, row, column):
                            playerData.board.addTile(tile, row, column, False) #get ready to test more deeply
                            
                            if not isinstance(tile.followRoute(routeSide)[0], OuterStations): #we're NOT going to connect to the border
                                abort=False
                                for threat in playerData.opponentsTiles: #we're going to make sure no opponent could shut this down
                                    for newRotation in range(4):
                                        newEndOfLine=tile.followRoute(routeSide)
                                        newRow, newColumn=playerData.board.lookupTileCoordinates(newEndOfLine[0])
                                        newRouteSide=newEndOfLine[1]
                                        threateningTile=playerData.makeTile(threat, newRotation)
                                        if not playerData.board.lookupTile(newRow, newColumn): #nothing here yet
                                            playerData.board.addTile(threateningTile, newRow, newColumn, False) #populate this with the board's knowledge
                                            if playerData.board.lookupTileCoordinates(threateningTile.neighborOnSide(newRouteSide))==(row, column): #this is adjacent to the tile we're trying to place
                                                threateningTile.addBorderingTile(tile, newRouteSide, False) #make it aware of the tile we were planning on placing
                                            if threateningTile.routeComplete(newRouteSide): #we could be thwarted
                                                abort=True
                                                break
                                if abort:
                                    break #this move would be no good; let's try a different rotation/tile
                                
                                playerData.board.addTile(tile, row, column) #commit/actually add it to the board
                                return playerData, PlayerMove(playerData.playerId, (row, column), playerData.currentTile, rotation)
                    break
    
    #go on the offense: shut down an opponent's track
    #TODO end longer tracks over shorter ones
    attacks=[] #stores (row, col, rotation, delta-score)
    for station in range(1, 33):
        if playerData.trackOwner(station)!=playerData.playerId and not playerData.board.routeIsComplete(station) and playerData.board.calculateTrackScore(station): #this isn't ours, has been started, and is unfinished
            endOfLine=playerData.board.followRoute(station)
            row, column=playerData.board.lookupTileCoordinates(endOfLine[0])
            routeSide=endOfLine[1]
            bestRotation=None #stores (rotation, delta-score)
            for rotation in range(4):
                tile=playerData.makeTile(playerData.currentTile, rotation)
                if playerData.board.validPlacement(tile, row, column): #this would be legal
                    playerData.board.addTile(tile, row, column, False)
                    if tile.routeComplete(routeSide): #we could complete this track to bother our opponent
                        deltaScore=0
                        
                        #check what else is happening at this location
                        abort=False
                        for neighbor in range(4):
                            if isinstance(tile.neighborOnSide(neighbor), ConnectedTile) and neighbor!=routeSide: #there could be a track here and this isn't the side we're primarily worried about
                                trackNum=playerData.board.lookupTrackNumber(tile.neighborOnSide(neighbor), neighbor)
                                endOfLine=tile.followRoute(neighbor)
                                if playerData.trackOwner(trackNum)==playerData.playerId: #one of our tracks passes through
                                    if isinstance(endOfLine, OuterStations): #we're going to end one of our tracks on an edge!
                                        abort=True
                                        break
                                elif isinstance(endOfLine, OuterStations): #they would be finished
                                    deltaScore+=tile.tabulateScore(neighbor)
                                elif isinstance(endOfLine, PowerStation): #they would be power-finished
                                    deltaScore+=playerData.board.calculateTrackScore(trackNum)+tile.tabulateScore(neighbor)*2 #score doubled
                                    
                        if abort:
                            continue #let's not use this rotation...
                        
                        if isinstance(tile.followRoute(routeSide), OuterStations): #no doubling to deal with
                            deltaScore+=tile.tabulateScore(routeSide)
                        else:
                            deltaScore+=playerData.board.calculateTrackScore(station)+tile.tabulateScore(neighbor)*2 #score doubled
                        if not bestRotation or deltaScore<bestRotation[1]: #we want to minimize their score
                            bestRotation=(rotation, deltaScore)
            if bestRotation: #we found at least one good move
                attacks.append((row, column, bestRotation[0], bestRotation[1])) #keep the best option for this tile
    attacks.sort(key=lambda possibleMove: possibleMove[3])
    if len(attacks):
        playerData.board.addTile(playerData.makeTile(playerData.currentTile, attacks[0][2]), attacks[0][0], attacks[0][1])
        return playerData, PlayerMove(playerData.playerId, (attacks[0][0], attacks[0][1]), playerData.currentTile, attacks[0][2])
    
    #score some points: extend one of our tracks
    #TODO check to make sure we don't accidently complete another one of our stations (write a method to reuse the code from above?)
    for highScoringTrack in playerData.ourRemainingStations: #attempt 1: put it where we want
        endOfLine=playerData.board.followRoute(stationId(highScoringTrack))
        row, column=playerData.board.lookupTileCoordinates(endOfLine[0]) #where could we place the tile to extend this route?
        routeSide=endOfLine[1] #on which side of the new tile is the track that we're extending?
        for rotation in range(4):
            tile=playerData.makeTile(rotation=rotation) #make one of whatever type of tile we've been given
            if playerData.board.validPlacement(tile, row, column):
                playerData.board.addTile(tile, row, column, False) #get ready to test this tile
                if not isinstance(tile.followRoute(routeSide)[0], OuterStations): #we're NOT going to connect to the border
                    abort=False
                    for threat in playerData.opponentsTiles: #we're going to make sure no opponent could shut this down
                        for newRotation in range(4):
                            #FIXME there seems to be a bug in here:
                            newEndOfLine=tile.followRoute(routeSide)
                            newRow, newColumn=playerData.board.lookupTileCoordinates(newEndOfLine[0])
                            newRouteSide=newEndOfLine[1]
                            threateningTile=playerData.makeTile(threat, newRotation)
                            if not playerData.board.lookupTile(newRow, newColumn): #nothing here yet
                                playerData.board.addTile(threateningTile, newRow, newColumn, False) #populate this with the board's knowledge
                                if playerData.board.lookupTileCoordinates(threateningTile.neighborOnSide(newRouteSide))==(row, column): #this is adjacent to the tile we're trying to place
                                    threateningTile.addBorderingTile(tile, newRouteSide, False) #make it aware of the tile we were planning on placing
                                if threateningTile.routeComplete(newRouteSide): #we could be thwarted
                                    abort=True
                                    break
                        if abort:
                            break #this move would be no good; let's try a different rotation/tile
                        
                        playerData.board.addTile(tile, row, column) #commit/actually add it to the board
                        return playerData, PlayerMove(playerData.playerId, (row, column), playerData.currentTile, rotation)
    
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
                return playerData, PlayerMove(playerData.playerId, (location[0], location[1]), playerData.currentTile, rotation)
    
    playerData.board.addTile(playerData.makeTile(), unoccupiedCoordinates[0][0], unoccupiedCoordinates[0][1], rotation)
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
        playerData.opponentsTiles=['' for _ in range(self.numPlayers)] #it's a new round and our opponents will have new tiles
    else: #we're looking at someone else's move
        playerData.board.addTile(playerData.makeTile(playerMove.tileName, playerMove.rotation), playerMove.position[0], playerMove.position[1]) #keep track of this tile's location
        playerData.opponentsTiles[playerMove.playerId]=nextTile #remember this player's next tile
    
    if playerData.numPlayers==1 or (playerMove and playerMove.playerId==(playerData.playerId-1)%playerData.numPlayers): #we're either all alone or we'll be up next
        playerData.updateOurStations() #keep watch on our progress and score
    
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
