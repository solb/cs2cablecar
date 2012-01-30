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
    __slots__ = ('logger', 'playerId', 'currentTile', 'numPlayers', 'board', 'ourRemainingStations')
    """
    Our data members:
        board - stores the tiles
        ourRemainingStations - contains the numbers (1-32) of our incomplete tracks and their scores
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
        
        #which tracks are ours?
        self.ourRemainingStations=[]
        for station in range(32//self.numPlayers):
            self.ourRemainingStations.append([station*numPlayers+playerId+1, 0])
    
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
    
    def trackOwner(self, trackId): #TODO this is wrong for some numbers of players!
        """
        trackOwner: int -> int
        Returns the player ID of the owner of the track with the specified track ID.
            trackId - the track ID (1-32)
        """
        return (trackId-1)%self.numPlayers
    
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
