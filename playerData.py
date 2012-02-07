"""
Cable Car: Student Computer Player

A modified sample class we have chosen to use to hold our state data
Author: Adam Oest (amo9149@rit.edu)
Author: Solomon Boucher (slb1566@rit.edu)
Author: Brad Bensch (brb7020@rit.edu)
"""
from board import *

######
#These functions are intended for accessing the information stored in PlayerData.ourRemainingStations
######
def stationId(remainingStationsMember, newValue=-1):
    """
    stationId: list(int) -> int
    Gets or sets the first element of the provided list
        remainingStationsMember - list of length 2
        newValue - the value to which to set the element, or -1 to instead get its value
    """
    if newValue!=-1:
        remainingStationsMember[0]=newValue
    
    return remainingStationsMember[0]

def stationScore(remainingStationsMember, newValue=-1):
    """
    stationId: list(int) -> int
    Gets or sets the second element of the provided list
        remainingStationsMember - list of length 2
        newValue - the value to which to set the element, or -1 to instead get its value
    """
    if newValue!=-1:
        remainingStationsMember[1]=newValue
    
    return remainingStationsMember[1]

class PlayerData(object):
    __slots__ = ('logger', 'playerId', 'currentTile', 'numPlayers', 'board', 'stationOwners', 'ourRemainingStations', 'opponentsTiles', 'mayMoveIllegally')
    """
    Our data members:
        board - stores the tiles
        stationOwners - contains the owner of each track, indexed by track *(0-31)*
            access via: PlayerData.trackOwner(...)
        ourRemainingStations - contains the numbers (1-32) of our incomplete tracks and their scores
            access via: stationId(...), stationScore(...)
        opponentsTiles - a list of our opponents' next tile letters, indexed by player ID
            NOTE: our tile and any eliminated opponents' tiles are set to ''
        mayMoveIllegally - a list of who may legally make an invalid move, indexed by player ID
    """
    
    def __init__(self, logger, playerId, currentTile, numPlayers):
        """
        __init__: PlayerData * Engine.Logger * int * NoneType * int -> None
        Constructs and returns an instance of PlayerData.
            self - new instance
            logger - the engine logger
            playerId - my player ID (0-5)
            currentTile - my current hand tile (initially None)
            numPlayers - number of players in game (1-6)
        """
        
        self.logger = logger
        self.playerId = playerId
        self.currentTile = currentTile
        self.numPlayers = numPlayers
        
        self.board=Board()
        
        #who owns each given track?
        if numPlayers==1:
            self.stationOwners=[0 for _ in range(32)]
        elif numPlayers==2:
            self.stationOwners=[num%2 for num in range(32)]
        elif numPlayers==3:
            self.stationOwners=[0, 1, 2, 0, 2, 0, 1, 2,\
                                1, 2, 0, 1, 2, 1, 0,-1,\
                               -1, 2, 1, 0, 2, 1, 0, 2,\
                                0, 2, 1, 0, 1, 2, 0, 1]
        elif numPlayers==4:
            self.stationOwners=[2, 3, 1, 0, 3, 2, 0, 1,\
                                3, 2, 0, 1, 2, 3, 1, 0,\
                                3, 2, 1, 0, 2, 3, 0, 1,\
                                2, 3, 0, 1, 3, 2, 1, 0]
        elif numPlayers==5:
            self.stationOwners=[0, 3, 2, 4, 0, 1, 2, 4,\
                                3, 0, 4, 1, 3, 0, 2,-1,\
                               -1, 1, 2, 4, 3, 0, 1, 4,\
                                2, 3, 1, 0, 2, 3, 4, 1]
        elif numPlayers==6:
            self.stationOwners=[0, 1, 4, 2, 0, 3, 5, 2,\
                                4, 0, 1, 5, 4, 2, 3,-1,\
                               -1, 1, 0, 3, 2, 5, 4, 3,\
                                1, 2, 0, 5, 1, 4, 3, 5]
                
        #which tracks are ours?
        self.ourRemainingStations=[]
        for station in range(len(self.stationOwners)):
            if self.stationOwners[station]==playerId: #this one's ours!
                self.ourRemainingStations.append([station+1, 0])
        
        self.opponentsTiles=['' for _ in range(numPlayers)]
        self.updateLegalConstraints()
    
    def makeTile(self, tileName='', rotation=0):
        """
        makeTile: str * int -> ConnectedTile
        Returns an object to represent the specified tile and rotation
            tileName - the type of tile, 'a'-'j' (default is our current tile)
            rotation - the tile's rotation, 0-3
        """
        if tileName=='':
            tileName=self.currentTile
        
        if tileName=='a':
            return TileA(rotation)
        elif tileName=='b':
            return TileB(rotation)
        elif tileName=='c':
            return TileC(rotation)
        elif tileName=='d':
            return TileD(rotation)
        elif tileName=='e':
            return TileE(rotation)
        elif tileName=='f':
            return TileF(rotation)
        elif tileName=='g':
            return TileG(rotation)
        elif tileName=='h':
            return TileH(rotation)
        elif tileName=='i':
            return TileI(rotation)
        else:
            return TileJ(rotation)
    
    def trackOwner(self, trackId):
        """
        trackOwner: int -> int
        Returns the player ID of the owner of the track with the specified track ID, or -1 if no one owns this track.
            trackId - the track ID (1-32)
        """
        return self.stationOwners[trackId-1]
    
    def routeInDanger(self, track, attacker=-1): #TODO We currently allow others to connect our routes to PowerStation s; should we make this optional?
        """
        routeInDanger: int * int -> bool
        Returns whether the specified attacker--or any player besides us if none specified--could connect the specified track--in its current state--to the board's edge in a single turn
            track - the ID of the track about which we're worried
            attacker - the ID of the player who might end the track, or all other players by default
        pre: The specified route is not yet complete, and the specified player actually has another move.
        """
        if attacker==-1: #we'll need to check all players
            for enemy in range(self.numPlayers):
                if self.opponentsTiles[enemy] and self.routeInDanger(track, enemy): #this player is an opponent with a move to make, and poses a threat to this route
                    return True
            return False
        else:
            if attacker==self.playerId: #WE are the attacker!
                tileType=self.currentTile
            else:
                tileType=self.opponentsTiles[attacker]
            routeEnd=self.board.followRoute(track)
            row, column=self.board.lookupTileCoordinates(routeEnd[0])
            side=routeEnd[1]
            for rotation in range(4):
                tile=self.makeTile(tileType, rotation)
                if self.board.validPlacement(tile, row, column) or self.mayMoveIllegally[attacker]: #move would be valid or would have just cause not to be
                    self.board.addTile(tile, row, column)
                    vulnerable=isinstance(tile.followRoute(side)[0], OuterStations)
                    self.board.removeTile(row, column)
                    if vulnerable:
                        return True
            return False
    
    def tileJeopardizesOurRoutes(self, row, column, allowCompletion=-1): #TODO We currently allow others to connect our routes to PowerStation s; should we make this optional?  Won't we sometimes want to be able to complete multiple tracks at once?
        """
        tileJeopardizesOurRoutes: int * int * int -> bool
        Returns whether the placement of the tile at the specified coordinates connected any of our routes to the edge or even placed any of them in danger's way
            row - r-coord (0-7)
            col - c-coord (0-7)
            allowCompletion - the side--if any--on which to permit a completion
        pre: A tile has already been placed at the specified coordinates.
        """
        for side in range(4):
            if side!=allowCompletion: #this isn't the side we were aiming to complete...
                if isinstance(self.board.lookupTile(row, column).followRoute(side)[0], OuterStations): #this opened a new path to the edge, so we need to reaffirm the safety of *all* our stations
                    for track in self.ourRemainingStations:
                        if isinstance(self.board.followRoute(stationId(track))[0], OuterStations) or self.routeInDanger(stationId(track)): #one of our remaining stations was either inadvertently completed or is now at risk
                            return True
                else: #we only need to check those of our stations that pass through this tile
                    route=self.board.lookupTrackNumber(self.board.lookupTile(row, column), self.board.lookupTile(row, column).adjacentSide(side))
                    
                    if route==-1 or self.trackOwner(route)!=self.playerId: #this isn't a real route (yet) or someone we don't care about owns it
                        continue
                    else: #this is one of our hard-earned routes
                        if isinstance(self.board.followRoute(route)[0], OuterStations) or self.routeInDanger(route): #one of our hard-earned stations was either inadvertently completed or is now at risk
                            return True
        return False
    
    ######
    #These functions are intended to be called regularly in order to update our recorded information.
    ######
    def updateOurStations(self):
        """
        updateOurStations
        Stops us from considering our completed stations and updates the scores of those on which we are still working
        post: ourRemainingStations is sorted in descending order by score, then in ascending order by ID number.
        """
        deletionStack=[]
        for station in range(len(self.ourRemainingStations)):
            if(self.board.routeIsComplete(stationId(self.ourRemainingStations[station]))):
                deletionStack.append(station) #flag this track for deletion
            else: #track may still be extended
                stationScore(self.ourRemainingStations[station], self.board.calculateTrackScore(stationId(self.ourRemainingStations[station]))) #update our record of the track's score
        
        while len(deletionStack):
            del self.ourRemainingStations[deletionStack.pop()]
        self.ourRemainingStations.sort(key=stationScore, reverse=True) #sort by score
    
    def updateLegalConstraints(self):
        """
        updateLegalConstratins
        Updates the list of who may legally make an invalid move
        post: mayMoveIllegally is up to date.
        """
        self.mayMoveIllegally=[True for _ in range(self.numPlayers)]
        for player in range(self.numPlayers):
            if player==self.playerId:
                tileName=self.currentTile
            else:
                tileName=self.opponentsTiles[player]
            if tileName: #we know of this player's next tile
                for row in range(8):
                    for column in range(8):
                        for rotation in range(4):
                            if self.board.validPlacement(self.makeTile(tileName, rotation), row, column): #this guy has no excuse but to make a legal move
                                self.mayMoveIllegally[player]=False
                                break
                        if not self.mayMoveIllegally[player]:
                            break
                    if not self.mayMoveIllegally[player]:
                        break
    
    def __str__(self):
        """
        __str__: PlayerData -> string
        Returns a string representation of the PlayerData object.
            self - the PlayerData object
        """
        result = "PlayerData= " \
                    + "playerId: " + str(self.playerId) \
                    + ", currentTile: " + str(self.currentTile) \
                    + ", numPlayers:" + str(self.numPlayers)
                
        # add any more string concatenation for your other slots here
        
        return result
