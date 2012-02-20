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
    __slots__ = ('logger', 'playerId', 'currentTile', 'numPlayers', 'board', 'stationOwners', 'ourRemainingStations', 'opponentsTiles', 'mayMoveIllegally', 'POWER_STATION_THRESHOLD', 'totalKills', 'totalHits', 'dangerousness', 'ourGift', 'ourGains')
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
        POWER_STATION_THRESHOLD - the gain we'd need to see before we'd complete one of our routes to a power station
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
    
    def routeInDanger(self, track, attacker=-1, disallowLowScore=False):
        """
        routeInDanger: int * int -> bool
        Returns whether the specified attacker--or any player besides us if none specified--could connect the specified track--in its current state--to the board's edge in a single turn.  If we are the attacker or we are checking all opponents, we also check whether someone could connect us to a power station for a low score.
            track - the ID of the track about which we're worried
            attacker - the ID of the player who might end the track, or all other players by default
            disallowLowScore - whether to prevent low-scoring powerstation connections
        pre: The specified route is not yet complete, and the specified player actually has another move.
        """
        if attacker==-1: #we'll need to check all players
            for enemy in range(self.numPlayers):
                if self.opponentsTiles[enemy] and self.routeInDanger(track, enemy, True): #this player is an opponent with a move to make, and poses a threat to this route
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
                    endpoint=tile.followRoute(side)[0]
                    vulnerable=isinstance(endpoint, OuterStations)
                    if disallowLowScore or attacker==self.playerId:
                        vulnerable=vulnerable or (isinstance(endpoint, PowerStation) and self.board.calculateTrackScore(track)/2<self.POWER_STATION_THRESHOLD)
                    self.board.removeTile(row, column)
                    if vulnerable:
                        return True
            return False
    
    def tileJeopardizesOurRoutes(self, row, column, acceptableGain=0, allowCompletion=-1):
        """
        tileJeopardizesOurRoutes: int * int * int * int -> bool
        Returns whether the placement of the tile at the specified coordinates connected any of our routes to the edge or even placed any of them in danger's way
            row - r-coord (0-7)
            col - c-coord (0-7)
            acceptableGain - only connect this route to a power station if it would score at least this many points for each of our tracks that it completes
            allowCompletion - the side--if any--on which to permit a completion
        pre: A tile has already been placed at the specified coordinates.
        """
        for side in range(4):
            if side!=allowCompletion:
                tile=self.board.lookupTile(row, column)
                route=self.board.lookupTrackNumber(tile, tile.adjacentSide(tile.nextTileSide(side)))
                if route==-1 or self.trackOwner(route)!=self.playerId: #this isn't a real route (yet) or someone we don't care about owns it
                    continue
                else: #this is one of our hard-earned routes
                    endpoint=self.board.followRoute(route)[0]
                    if isinstance(endpoint, OuterStations) or (isinstance(endpoint, PowerStation) and self.board.calculateTrackScore(route)/2<self.POWER_STATION_THRESHOLD) or self.routeInDanger(route): #one of our hard-earned stations was either inadvertently completed or is now at risk
                        return True
        return False
    
    def possibleTrackExtensions(self, track, completeTrack):
        """
        possibleTrackExtensions: int * bool -> list(int, int, int, int)
        Returns a list of the permissible uses of the current tile in order to extend the specified track and either complete or not complete it, all while maintaining the completeness and safety of our own stations; the list is of the form (row, column, rotation, old_score, delta_score)
            track - the track to extend
            completeTrack - our goal, whether it be to complete the track or not to complete it
        """
        row, column=self.board.lookupTileCoordinates(self.board.followRoute(track)[0])
        oldScore=self.board.calculateTrackScore(track)
        options=[] #stores (rotation, score)
        for rotation in range(4):
            ourTile=self.makeTile(rotation=rotation)
            if self.board.validPlacement(ourTile, row, column) or (not self.board.lookupTile(row, column) and self.mayMoveIllegally[self.playerId]): #we're legal or allowed not to be
                self.board.addTile(ourTile, row, column)
                endpoint=self.board.followRoute(track)[0]
                if isinstance(endpoint, OuterStations)==completeTrack or isinstance(endpoint, PowerStation)==completeTrack: #this rotation completes it
                    if not self.tileJeopardizesOurRoutes(row, column, self.POWER_STATION_THRESHOLD): #we haven't done anything significant to our own routes at the same time
                        options.append([row, column, rotation, oldScore, self.board.calculateTrackScore(track)-oldScore])
                    #else:
                        #print 'NB: Placing at '+str((row, column))+' w/ rotation '+str(rotation)+' would jeopardize our own route'
                self.board.removeTile(row, column)
        return options
    
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
                #print 'They\'ve given us a broadside!'
            else: #track may still be extended
                stationScore(self.ourRemainingStations[station], self.board.calculateTrackScore(stationId(self.ourRemainingStations[station]))) #update our record of the track's score
        
        while len(deletionStack):
            del self.ourRemainingStations[deletionStack.pop()]
        self.ourRemainingStations.sort(key=stationScore, reverse=True) #sort by score
    
    def updateLegalConstraints(self):
        """
        updateLegalConstraints
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
                    
    def firstTurn(self):
        """
        firstTurn
        Returns True or False if we have the first turn
        """
        occupiedFlag = True
        for row in range(8): #Are any tiles placed yet?
            if occupiedFlag == False:
                break
            for column in range(8):
                if occupiedFlag == False:
                    break
                if self.board.lookupTile(row, column) != None:
                    if row == 3 and column == 3:
                        break
                    elif row == 3 and column == 4:
                        break
                    elif row == 4 and column == 3:
                        break
                    elif row == 4 and column == 4:
                        break
                    else:
                        occupiedFlag = False
        return occupiedFlag
            
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

class PotentialMove(object):
    __slots__=('row', 'column', 'rotation', 'tracks', 'ourLosses', 'enemyLosses', 'deltaEndangerment', 'ourGains', 'enemyGains')
    """
    PotentialMove: PlayerData * int * int * int * list(PotentialTrack)
    Represents a move that we could make and contains its repercussions
        row - r-coordinate of move
        column - c-coordinate of move
        rotation - rotation of our current tile
        tracks - PotentialTrack objects for each route that goes through this tile
    """
    
    def __init__(self, data, row, column, rotation):
        """
        Creates a PotentialMove instance and calculates the statistics for the proposed move
            playerData - PlayerData instance
            row, column - coordinates of new move
            rotation - rotation of our tile
        """
        self.row, self.column, self.rotation=row, column, rotation
        
        tile=data.makeTile(data.currentTile, rotation)
        data.board.addTile(tile, row, column, False)
        
        #scope the area to discover routes through this track:
        self.tracks=[]
        for border in range(4):
            if isinstance(tile.neighborOnSide(border), OuterStations):
                self.tracks.append(PotentialTrack(data.board.lookupTrackNumber(data.board.lookupTile(row, column, True), border)))
            elif isinstance(tile.neighborOnSide(border), ConnectedTile):
                trackNum=data.board.lookupTrackNumber(tile.neighborOnSide(border), border)
                if trackNum!=-1:
                    self.tracks.append(PotentialTrack(trackNum))
                else: #there are places where routes could be, but no track connects to them
                    continue
            else: #no routes through this tile
                continue
            self.tracks[-1].ours=data.trackOwner(self.tracks[-1].number)==data.playerId #do we own this?
            if self.tracks[-1].ours:
                self.tracks[-1].wasVulnerable=data.routeInDanger(self.tracks[-1].number)
            self.tracks[-1].oldScore=data.board.calculateTrackScore(self.tracks[-1].number) #store the old score
        
        #collect data on the surrounding routes:
        data.board.addTile(tile, row, column)
        for changedTrack in self.tracks:
            changedTrack.completed=data.board.routeIsComplete(changedTrack.number)
            if not changedTrack.completed:
                if changedTrack.ours:
                    changedTrack.nowVulnerable=data.routeInDanger(changedTrack.number) #someone else could attack this
                elif data.numPlayers>2: #someone else's; can anyone else harm it?
                    for enemy in range(data.numPlayers):
                        if enemy!=data.playerId and enemy!=data.trackOwner(changedTrack.number) and data.routeInDanger(changedTrack.number, enemy): #someone could connect this straight to the edge
                            changedTrack.nowVulnerable=True
                            break
            changedTrack.deltaScore=data.board.calculateTrackScore(changedTrack.number)-changedTrack.oldScore
        data.board.removeTile(row, column)
        
        self.ourLosses, self.enemyLosses, self.deltaEndangerment, self.ourGains, self.enemyGains=0, 0, 0, 0, 0
        #summarize our findings:
        for changedTrack in self.tracks:
            if changedTrack.ours:
                if changedTrack.completed:
                    self.ourLosses+=1
                
                if not changedTrack.wasVulnerable and changedTrack.nowVulnerable:
                    self.deltaEndangerment+=1
                elif changedTrack.wasVulnerable and not changedTrack.nowVulnerable:
                    self.deltaEndangerment-=1
                #otherwise we're neither more in danger not less in danger than we were
                
                self.ourGains+=changedTrack.deltaScore
            else: #enemy track
                if changedTrack.completed:
                    self.enemyLosses+=1
                
                self.enemyGains+=changedTrack.deltaScore
    
    def __repr__(self):
        """
        __repr__ -> str
        Returns a string representation of this thing
        """
        return str((self.row, self.column))+' '+str(self.rotation)+': '+'LOSSES: us '+str(self.ourLosses)+' them '+str(self.enemyLosses)+'; ENDANGERMENT: '+str(self.deltaEndangerment)+'; GAINS: us '+str(self.ourGains)+' them '+str(self.enemyGains)+'\n'

class PotentialTrack(object):
    __slots__=('number', 'ours', 'completed', 'wasVulnerable', 'nowVulnerable', 'oldScore', 'deltaScore')
    """
    PotentialTrack: int * bool * bool * bool * int * int
    Represents the possible new state of a track
        number - the track number
        ours - whether the track belongs to us
        completed - whether the track was completed
        vulnerable - whether the track is now vulnerable to emeny attack
        oldScore - the track's original score
        deltaScore - the difference in the track's score
    """
    def __init__(self, number):
        """
        Creates a PotentialTrack instance
            number - the track number
        """
        self.number=number
        self.ours, self.completed, self.wasVulnerable, self.nowVulnerable=False, False, False, False
        self.oldScore, self.deltaScore=0, 0
