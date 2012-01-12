"""
Cable Car: Student Computer Player

A sample class you may use to hold your state data
Author: Adam Oest (amo9149@rit.edu)
Author: Solomon Boucher (slb1566@rit.edu)
Author: Brad Bensch (brb7020@rit.edu)
Author: YOUR NAME HERE (your email address)
"""
from copy import deepcopy

class PlayerData(object):
    """A sample class for your player data"""
    
    # Add other slots as needed
    __slots__ = ('logger', 'playerId', 'currentTile', 'numPlayers', 'board')
    
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
        
        # initialize any other slots you require here
        
        self.board=Board()
        
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

class Board(object):
    """
    Board: lst(lst(Tile)) * Cars
    Represents the board, the tiles on it, and the cable car stations around its perimeter
        board - a 2-D list of the placeable ConnectedTiles and fixed PowerStation tiles; allows random access
        cars - a Cars object representing the cable car stations; allows sequential route tracing
    """
    __slots__=('board', 'cars')
    
    def __init__(self):
        """
        __init__
        Constructs and returns an instance of Board
        """
        emptyTile=Tile()
        self.board=[[emptyTile for _ in range(8)] for _ in range(8)]
        powerPlace=PowerStation()
        for row in [self.board[3], self.board[4]]:
            for col in [3, 4]:
                row[col]=powerPlace #place the power stations in the center of the board
        self.cars=Cars()
    
    def _linkTileSide(self, newResident, neighboringRow, neighboringCol, side, makePermanent=True):
        """
        _linkTileSide: ConnectedTile * int * int * int
        Links a newly-placed tile with the surrounding tiles
            newResident - the new tile to be linked
            neighboringRow - the r-coordinate of the existing tile with which to link (0-7)
            neighboringCol - the c-coordinate of the existing tile with which to link (0-7)
            side - which side of newResident this (r,c) location is on (0-3)
            makePermanent - whether to create mutual, unbreakable links; alternative is to solely modify the provided tile
        """
        if neighboringRow<0 or neighboringRow>=len(self.board): #newResident on the top or bottom board edge
            self.cars.layTrack(newResident, side, neighboringCol, makePermanent) #link station to this tile
        elif neighboringCol<0 or neighboringCol>=len(self.board[neighboringRow]): #on the left or right edge
            self.cars.layTrack(newResident, side, neighboringRow, makePermanent) #link station to this tile
        else: #not on the edge of the board
            newResident.addBorderingTile(self.board[neighboringRow][neighboringCol], side, makePermanent) #link with another ConectedTile
    
    def addTile(self, resident, row, column, makePermanent=True):
        """
        addTile: ConnectedTile * int * int -> bool
        Places a new tile on the board, returning whether the operation succeeded (didn't clash with an existing tile)
            resident - the new tile to be placed
            row - the r-coordinate (0-7)
            column - the c-coordinate (0-7)
            makePermanent - whether to create mutual, unbreakable links; alternative is to solely modify the provided tile
        pre: This must be a valid move!
        """
        if self.board[row][column]: #there's already something there!
            return False
        
        if makePermanent:
            self.board[row][column]=resident
        
        self._linkTileSide(resident, row-1, column, 0, makePermanent) #link with the above tile
        self._linkTileSide(resident, row, column+1, 1, makePermanent) #link with the right tile
        self._linkTileSide(resident, row+1, column, 2, makePermanent) #link with the left tile
        self._linkTileSide(resident, row, column-1, 3, makePermanent) #link with the below tile
        return True
    
    def lookupTile(self, row, column):
        """
        lookupTile: int * int -> ConnectedTile or None
        Returns the ConnectedTile or PowerStation at the coordinates (row,column), or None if there is no tile there
            row - the row (0-7)
            column - the colum (0-7)
        """
        tile=self.board[row][column]
        
        if tile:
            return tile
        else:
            return None
    
    def lookupTrack(self, whichStation):
        """
        lookupTrack: int -> ConnectedTile or None
        Returns the ConnectedTile attached to the specified cable car station, or None if there's nothing attached
            whichStation - the cable car station (1-32)
        """
        track=self.cars.rideTrack(whichStation-1)
        
        if track:
            return track
        else:
            return None
    
    def routeIsComplete(self, whichStation):
        """
        routeIsComplete: int -> bool
        Checks whether the route originating at the specified cable car station is actually connected to anything at the other end
            whichStation - the cable car station (1-32)
        """
        return self.cars.routeComplete(whichStation-1)
    
    def calculateTrackScore(self, whichStation):
        """
        calculateTrackScore: int -> int
        Returns the score of the route originating at the specified cable car station
            whichStation - the cable car station (1-32)
        """
        return self.cars.calculateScore(whichStation-1)
    
    def _sideConnectsToEdge(self, newTile, side):
        """
        _sideConnectsToEdge: ConnectedTile * int -> bool
        Checks whether the specified side of this tile connects to the edge of the board
            newTile - the proposed new tile
            side - which side of newTile we're starting from (0-3)
        """
        return isinstance(newTile.lookupDestination(side), OuterStations) #connects to an edge
    
    def _sideConnectsToPlayerPlacedTile(self, newTile, side):
        """
        _sideConnectsToPlayerPlacedTile: ConnectedTile * int -> bool
        Checks whether the specified side of this tile connects to a tile placed by a player
            newTile - the proposed new tile
            side - which side of newTile we're starting from (0-3)
        """
        return isinstance(newTile.lookupDestination(side), ConnectedTile) #connects to an edge
    
    def validPlacement(self, tile, row, column):
        """
        validPlacement: ConnectedTile * int * int -> bool
        Returns whether or not the specified tile may be placed at the proposed coordinates
            tile - the tile to be placed
            row - isn't it obvious? (0-7)
            column - likewise (0-7)
        """
        tile=deepcopy(tile)
        
        if not self.addTile(tile, row, column, False): #unoccupied location
            return False
        
        atLeastOneOccupiedSide=False
        
        if row-1<0: #on the top edge of the board
            if self._sideConnectsToEdge(tile, 0): #edge connects back to another station w/o leaving tile
                return False
            else:
                atLeastOneOccupiedSide=True
        else: #not on top edge
            if not atLeastOneOccupiedSide and self._sideConnectsToPlayerPlacedTile(tile, 0):
                atLeastOneOccupiedSide=True
        
        if column+1>=len(self.board[row]): #on the right edge of the board
            if self._sideConnectsToEdge(tile, 1): #edge connects back to another station w/o leaving tile
                return False
            else:
                atLeastOneOccupiedSide=True
        else: #not on right edge
            if not atLeastOneOccupiedSide and self._sideConnectsToPlayerPlacedTile(tile, 1):
                atLeastOneOccupiedSide=True
        
        if row+1>=len(self.board): #on the bottom edge of the board
            if self._sideConnectsToEdge(tile, 2): #edge connects back to another station w/o leaving tile
                return False
            else:
                atLeastOneOccupiedSide=True
        else: #not on bottom edge
            if not atLeastOneOccupiedSide and self._sideConnectsToPlayerPlacedTile(tile, 2):
                atLeastOneOccupiedSide=True
        
        if column-1<0: #on the top edge of the board
            if self._sideConnectsToEdge(tile, 3): #edge connects back to another station w/o leaving tile
                return False
            else:
                atLeastOneOccupiedSide=True
        else: #not on top edge
            if not atLeastOneOccupiedSide and self._sideConnectsToPlayerPlacedTile(tile, 3):
                atLeastOneOccupiedSide=True
        
        return atLeastOneOccupiedSide

class Cars(object):
    """
    Cars: lst(OuterStations)
    Represents *all* of the cable car stations that surround the playing board.
        stations - a list of the four OuterStations objects surrounding the board (length 4)
    """
    __slots__=('stations')
    
    def __init__(self):
        """
        __init__
        Constructs and returns an instance of Cars
        """
        self.stations=[OuterStations(rotation) for rotation in range(4)]
    
    def layTrack(self, neighbor, side, station, rememberTile=True):
        """
        layTrack: ConnectedTile * int * int
        Links a ConnectedTile that's being placed on the edge of the board to the appropriate OuterStations
            neighbor - the ConnectedTile that's being added on the edge of the board
            side - the ID of the correct OuterStations object
            station - the cable car station to which the link should be made (0-31)
            rememberTile - whether to retain the reference to this tile; alternative is to only tell the tile about us
        """
        if side/2: #bottom or left group of cable car stations
            station=7-station #reverse numbering scheme
        self.stations[side].addTrack(neighbor, station, rememberTile)
    
    def _terminal(self, station):
        """
        _terminal: int -> OuterStations
        Returns the terminal containing the desired cable car station (on which side of the board that station is located)
            station - the cable car station *(0-31)*
        NOTE: At this level, the cable car station is represented using a 0-based indexing system; this contrasts with the 1-based scheme used at all levels higher!
        """
        return self.stations[station/8]
    
    def rideTrack(self, car):
        """
        rideTrack: int -> Tile
        Returns the first tile of the track initiating at the specified cable car station
            car - the cable car station *(0-31)*
        NOTE: At this level, the cable car station is represented using a 0-based indexing system; this contrasts with the 1-based scheme used at all levels higher!
        """
        return self._terminal(car).lookupSource(car%8)
    
    def routeComplete(self, track):
        """
        routeComplete: int -> bool
        Checks whether the route originating at the specified cable car station is actually connected to anything at the other end
            track - the cable car station *(0-31)*
        NOTE: At this level, the cable car station is represented using a 0-based indexing system; this contrasts with the 1-based scheme used at all levels higher!
        """
        return self.rideTrack(track).routeComplete(self._terminal(track))
    
    def calculateScore(self, track):
        """
        calculateScore: int -> int
        Returns the score of the route originating at the specified cable car station
            track - the cable car station *(0-31)*
        NOTE: At this level, the cable car station is represented using a 0-based indexing system; this contrasts with the 1-based scheme used at all levels higher!
        """
        return self.rideTrack(track).tabulateScore(self._terminal(track), 0)

class Tile(object):
    """
    Tile: str * int
    Represents an empty spot where a game piece might be placed in the future
        type - a code representing the type of tile
        rotation - the tile's rotation (0-3)
    """
    __slots__=('type', 'rotation')
    
    def __init__(self):
        """
        __init__
        Constructs and returns an instance of Tile
        """
        self.type=''
        self.rotation=''
    
    def getType(self):
        """
        getType: -> str
        Returns the type of tile ('a'-'j')
        """
        return self.type
    
    def getRotation(self):
        """
        getRotation: -> int
        Returns the tile's rotation (0-3)
        """
        return self.rotation
    
    def routeComplete(self, _):
        """
        routeComplete: any -> bool
        This helper method is used to determine whether each Tile represents the end of its track, and if so, it returns whether it represents an ending that leaves the track complete.  This default implementation always replies that the route is incomplete.
            _ - ignored (included for compatibility with child classes' implementations)
        """
        return False
    
    def tabulateScore(self, _, runningScore):
        """
        tabulateScore: any * int -> int
        This helper method is used to determine each track's total score.  This particular default always returns the running score without incrementing it.
            _ - ignored (included for compatibility with child classes' implementations)
            runningScore - the running score
        """
        return runningScore
    
    def __nonzero__(self):
        """
        __nonzero__: -> bool
        This method indicates whether this Tile is a permanent, unmovable occupant of its spot.  This default implementation always replies that this Tile may be replaced with another.
        """
        return False
    
    def __repr__(self):
        """
        __repr__: -> str
        Returns the tile's type and rotation.  This function is intended primarily for debugging purposes.
        """
        return 'Tile '+self.type+' rotation '+str(self.rotation)

class OuterStations(Tile):
    """
    OuterStations: lst(ConnectedTile)
    Represents a group of *8* of the cable car stations that surround the playing board.
        borderedTiles - a list of the outermost ConnectedTiles along this edge of the board (length 8)
    NOTE: rotation indicates to *which side of its ConnectedTiles* this group links.
    """
    __slots__=('borderedTiles')
    
    def __init__(self, rotation):
        """
        __init__: int
        Constructs and returns and instance of OuterStations
            rotation - the stations' tiles' rotations (0-3)
        """
        Tile.__init__(self)
        self.type='os'
        self.rotation=rotation
        emptyTile=Tile()
        self.borderedTiles=[emptyTile for _ in range(8)]
    
    def addTrack(self, neighbor, substation, rememberTile=True):
        """
        addTrack: ConnectedTile * int
        Adds a ConnectedTile that is being placed on this edge of the board
            neighbor - the ConnectedTile to be linked
            substation - the index of the station to which the tile should be linked (0-7)
            rememberTile - whether to retain the reference to this tile; alternative is to only tell the tile about us
        """
        if rememberTile:
            self.borderedTiles[substation]=neighbor
        neighbor.addBorderingTile(self, self.rotation) #make connection mutual
    
    def lookupSource(self, substation):
        """
        lookupSource: int -> ConnectedTile
        Returns the ConnectedTile at this station
            substation - the index of the station containing the desired tile (0-7)
        """
        return self.borderedTiles[substation]
    
    def routeComplete(self, _):
        """
        routeComplete: any -> bool
        This helper method is used to determine whether each Tile represents the end of its track, and if so, it returns whether it represents an ending that leaves the track complete.  This override always replies that the route is complete.
            _ - ignored (included for compatibility with child classes' implementations)
        """
        return True

class PowerStation(Tile):
    """
    PowerStation
    Represents one of the special power stations in the middle of the playing board.
    """
    def __init__(self):
        """
        __init__
        Constructs and returns an instance of PowerStation
        """
        Tile.__init__(self)
        self.type='ps'
        self.rotation=0
    
    def routeComplete(self, _):
        """
        routeComplete: any -> bool
        This helper method is used to determine whether each Tile represents the end of its track, and if so, it returns whether it represents an ending that leaves the track complete.  This override always replies that the route is complete.
            _ - ignored (included for compatibility with child classes' implementations)
        """
        return True
    
    def tabulateScore(self, _, runningScore):
        """
        tabulateScore: any * int -> int
        This helper method is used to determine each track's total score.  This override always returns twice the running score in order to award the deserved 2x bonus.
            _ - ignored (included for compatibility with child classes' implementations)
            runningScore - the running score
        """
        return runningScore*2
    
    def __nonzero__(self):
        """
        __nonzero__: -> bool
        This method indicates whether this Tile is a permanent, unmovable occupant of its spot.  This override always replies that this Tile may not be replaced.
        """
        return True

class ConnectedTile(Tile):
    """
    ConnectedTile: * List(Tile) * List(int)
    Represents one of the playable track pieces.
        borderingTiles - a list of the adjacent tiles (length 4)
        internalConnections - a list of the tile-specific exit points for all entrance points (length 4)
    """
    __slots__=('borderingTiles', 'internalConnections')
    
    def __init__(self):
        """
        __init__
        Constructs and returns an instance of ConnectedTile
        """
        Tile.__init__(self)
        self.borderingTiles=[None for _ in range(4)]
        self.internalConnections=[]
    
    def _rotate(self, connectionsTemplate, rotation):
        """
        _rotate: List(int) * int
        Fixes a specific instance's connections, accounting for both the tile's type and its rotation.
            connectionsTemplate - the tile-specific internalConnections version for an unrotated instance (length 4)
            rotation - this instance's rotation (0-3)
        pre: internalConnections is an empty list (length 0).
        """
        self.rotation=rotation
        firstIndex=-rotation%len(connectionsTemplate) #start rotation indicies from the end
        for oldIndex in range(firstIndex, len(connectionsTemplate))+range(firstIndex): #go from the calculated start to the list's end, then loop from the beginning
            newIndex=len(self.internalConnections) #we'll be adding an index at the list's end
            self.internalConnections.append((newIndex+connectionsTemplate[oldIndex]-oldIndex)%len(connectionsTemplate)) #cycle the *differences* between each index and its target
    
    def addBorderingTile(self, neighbor, side, mutualConnection=True):
        """
        addBorderingTile: Tile, int
        Links this tile with that lying on the specified side.
            neighbor - the tile with which this one should be linked (a two-way link will only be created if this is a ConnectedTile)
            side - on which side of this tile neighbor is sitting (0-3)
            mutualConnection - whether to connect both ways iff neighbor is a ConnectedTile
        pre: neighbor is not in borderingTiles.
        """
        self.borderingTiles[side]=neighbor
        if mutualConnection and isinstance(neighbor, ConnectedTile):
            neighbor.borderingTiles[(side-2)%len(self.borderingTiles)]=self #make the connection mutual
    
    def neighborOnSide(self, side):
        """
        hasNeighborOnSide: int -> Tile
        Fetches the tile bordering the specified side of this one
            side - the side of this tile to check (0-3)
        """
        return self.borderingTiles[side]
    
    def _entryPoint(self, source):
        """
        _entryPoint: Tile -> int
        Calculates the side at which the tile source enters this one (0-3).
            source - the tile whose path is being followed
        pre: source is in borderingTiles.
        """
        return self.borderingTiles.index(source)
    
    def _exitPoint(self, entryPoint):
        """
        _exitPoint: int -> int
        Calculates the side from which the streetcar arriving at entryPoint will emerge (0-3).
            entryPoint - the slot at which this tile has been entered (0-3)
        """
        return self.internalConnections[entryPoint]
    
    def lookupDestination(self, source):
        """
        lookupDestination: (Tile or int) -> Tile
        Determines to which other tile this tile's path will lead if one is to start from specified neighboring tile or side of this tile.
            source - the neighboring tile from where wants to trace the path or side of this tile from where one wants to start (0-3)
        """
        if isinstance(source, Tile):
            return self.borderingTiles[self._exitPoint(self._entryPoint(source))]
        else:
            return self.borderingTiles[self._exitPoint(source)]
    
    def routeComplete(self, caller):
        """
        routeComplete: Tile -> bool
        This helper method is used to determine whether each Tile represents the end of its track, and if so, it returns whether it represents an ending that leaves the track complete.  This override always recurses to the destination Tile's implementation of this method and returns the result of that call.
            caller - a reference to the Tile that called this method
        """
        return self.lookupDestination(caller).routeComplete(self)
    
    def tabulateScore(self, caller, runningScore):
        """
        tabulateScore: Tile * int -> int
        This helper method is used to determine each track's total score.  This override always recurses to the destination Tile's implementation of this method, incrementing the score by 1, and returns the result of that call.
            caller - a reference to the Tile that called this method
            runningScore - the running score
        """
        return self.lookupDestination(caller).tabulateScore(self, runningScore+1)
    
    def __nonzero__(self):
        """
        __nonzero__: -> bool
        This method indicates whether this Tile is a permanent, unmovable occupant of its spot.  This override always replies that this Tile may not be replaced.
        """
        return True

class TileA(ConnectedTile):
    def __init__(self, rotation):
        """
        __init__: int
        Constructs and returns and instance of this class.
            rotation - the tile's rotation (0-3)
        """
        ConnectedTile.__init__(self)
        self.type='a'
        self._rotate([0, 3, 2, 1], rotation)

class TileB(ConnectedTile):
    def __init__(self, rotation):
        """
        __init__: int
        Constructs and returns and instance of this class.
            rotation - the tile's rotation (0-3)
        """
        ConnectedTile.__init__(self)
        self.type='b'
        self._rotate([1, 3, 0, 2], rotation)

class TileC(ConnectedTile):
    def __init__(self, rotation):
        """
        __init__: int
        Constructs and returns and instance of this class.
            rotation - the tile's rotation (0-3)
        """
        ConnectedTile.__init__(self)
        self.type='c'
        self._rotate([1, 2, 0, 3], rotation)

class TileD(ConnectedTile):
    def __init__(self, rotation):
        """
        __init__: int
        Constructs and returns and instance of this class.
            rotation - the tile's rotation (0-3)
        """
        ConnectedTile.__init__(self)
        self.type='d'
        self._rotate([0, 3, 1, 2], rotation)

class TileE(ConnectedTile):
    def __init__(self, rotation):
        """
        __init__: int
        Constructs and returns and instance of this class.
            rotation - the tile's rotation (0-3)
        """
        ConnectedTile.__init__(self)
        self.type='e'
        self._rotate([0, 1, 3, 2], rotation)

class TileF(ConnectedTile):
    def __init__(self, rotation):
        """
        __init__: int
        Constructs and returns and instance of this class.
            rotation - the tile's rotation (0-3)
        """
        ConnectedTile.__init__(self)
        self.type='f'
        self._rotate([2, 3, 0, 1], rotation)

class TileG(ConnectedTile):
    def __init__(self, rotation):
        """
        __init__: int
        Constructs and returns and instance of this class.
            rotation - the tile's rotation (0-3)
        """
        ConnectedTile.__init__(self)
        self.type='g'
        self._rotate([0, 1, 2, 3], rotation)

class TileH(ConnectedTile):
    def __init__(self, rotation):
        """
        __init__: int
        Constructs and returns and instance of this class.
            rotation - the tile's rotation (0-3)
        """
        ConnectedTile.__init__(self)
        self.type='h'
        self._rotate([3, 0, 1, 2], rotation)

class TileI(ConnectedTile):
    def __init__(self, rotation):
        """
        __init__: int
        Constructs and returns and instance of this class.
            rotation - the tile's rotation (0-3)
        """
        ConnectedTile.__init__(self)
        self.type='i'
        self._rotate([1, 2, 3, 0], rotation)

class TileJ(ConnectedTile):
    def __init__(self, rotation):
        """
        __init__: int
        Constructs and returns and instance of this class.
            rotation - the tile's rotation (0-3)
        """
        ConnectedTile.__init__(self)
        self.type='j'
        self._rotate([3, 2, 1, 0], rotation)
