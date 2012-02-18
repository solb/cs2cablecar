"""
Cable Car: Data Storage Solution

A fully-encapsulated system for keeping track of the board and its tiles.  The user will typically only need to use the Board class and the subclasses of ConnectedTile.
Author: Solomon Boucher (slb1566@rit.edu)
Author: Brad Bensch (brb7020@rit.edu)
"""
from copy import deepcopy

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
        self.cars=Cars()
        
        self.board=[[None for _ in range(8)] for _ in range(8)]
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                for side in range(4):
                    if (row==3 or row==4) and (col==3 or col==4):
                        self.board[row][col]=PowerStation()
                    else:
                        self.addTile(Tile(), row, col)
    
    def _linkTileSide(self, newResident, neighboringRow, neighboringCol, side, makePermanent=True):
        """
        _linkTileSide: Tile * int * int * int
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
        elif isinstance(newResident, ConnectedTile): #not on the edge of the board and may be linked
            newResident.addBorderingTile(self.board[neighboringRow][neighboringCol], side, makePermanent) #link with another ConectedTile
        elif isinstance(self.board[neighboringRow][neighboringCol], ConnectedTile): #newResident isn't a ConnectedTile, and this neighboring ConnectedTile doesn't know about it
            self.board[neighboringRow][neighboringCol].addBorderingTile(newResident, self.board[neighboringRow][neighboringCol].adjacentSide(side), False)
    
    def addTile(self, resident, row, column, makePermanent=True):
        """
        addTile: Tile * int * int -> bool
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
        self._linkTileSide(resident, row+1, column, 2, makePermanent) #link with the below tile
        self._linkTileSide(resident, row, column-1, 3, makePermanent) #link with the left tile
        return True
    
    def removeTile(self, row, column):
        """
        removeTile: int * int -> bool
        Removes the tile at the specified coordinates from the board, returning whether the operation succeeded (didn't try to remove part of the board itself)
            row - the r-coordinate (0-7)
            column - the c-coordinate (0-7)
        post: The tile that has been removed is the same as if it had been passed into addTile(...) in order to create a temporary link.
        """
        oldTile=self.board[row][column]
        if not isinstance(oldTile, ConnectedTile): #this is part of the board
            return False
        
        self.board[row][column]=Tile() #replace with placeholder
        self._linkTileSide(self.board[row][column], row-1, column, 0, True) #unlink from the above tile
        self._linkTileSide(self.board[row][column], row, column+1, 1, True) #unlink from the right tile
        self._linkTileSide(self.board[row][column], row+1, column, 2, True) #unlink from the below tile
        self._linkTileSide(self.board[row][column], row, column-1, 3, True) #unlink from the left tile
        return True
    
    def lookupTile(self, row, column, giveEmpty=False):
        """
        lookupTile: int * int -> ConnectedTile or None
        Returns the ConnectedTile or PowerStation at the coordinates (row,column), or None if there is no tile there
            row - the row (0-7)
            column - the colum (0-7)
            giveEmpty - whether to return the tile even if it's just a placeholder
        """
        tile=self.board[row][column]
        
        if tile or giveEmpty:
            return tile
        else:
            return None
    
    def lookupTrack(self, whichStation, giveEmpty=False):
        """
        lookupTrack: int -> ConnectedTile or None
        Returns the ConnectedTile attached to the specified cable car station, or None if there's nothing attached
            whichStation - the cable car station (1-32)
            giveEmpty - whether to return the tile even if it's just a placeholder
        """
        track=self.cars.rideTrack(whichStation-1)
        
        if track or giveEmpty:
            return track
        else:
            return None
    
    def lookupTileCoordinates(self, tile):
        """
        lookupTileCoordinates: Tile -> tuple(int) or None
        Returns the coordinates at which the supplied tile is located, or None if it isn't located.
            tile - the Tile being sought
        """
        for row in range(len(self.board)):
            if tile in self.board[row]:
                return row, self.board[row].index(tile)
        return None
    
    def lookupTrackNumber(self, tile, side):
        """
        lookupTrackNumber: Tile * int -> int
        Returns the cable car station (1-32) of the from which the track ending on the specified side of the specified tile originates.  If the route doesn't touch the edge of the board, the sentinel -1 is returned.
            tile - the ConnectedTile at the end of the route, or an empty Tile on the edge of the board
            side - the side of the next tile in the route (after the last one) to which the route connects (0-3)
        pre: tile must be on this board!
        """
        result=self.cars.reverseFollowRoute(tile, side)+1
        if not result: #invalid, meaning the route never touched the board's edge
            return -1
        else:
            return result
    
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
    
    def followRoute(self, whichStation):
        """
        followRoute: int -> tuple(Tile, int)
        Returns the tile to which this route connects and to which side of that tile it is linked
            whichStation - the cable car station (1-32)
        """
        return self.cars.followRoute(whichStation-1)
    
    def validPlacement(self, tile, row, column):
        """
        validPlacement: ConnectedTile * int * int -> bool
        Returns whether or not the specified tile may be placed at the proposed coordinates
            tile - the tile to be placed
            row - isn't it obvious? (0-7)
            column - likewise (0-7)
        """
        tile=deepcopy(tile)
        if not self.addTile(tile, row, column, False): #location already occupied
            return False
        
        atLeastOneOccupiedSide=False
        for side in range(4):
            neighbor=tile.neighborOnSide(side)
            if isinstance(neighbor, OuterStations) and isinstance(tile.lookupDestination(neighbor), OuterStations): #this tile would "short out" this station
                return False
            elif isinstance(neighbor, OuterStations) or isinstance(neighbor, ConnectedTile): #this tile is connected to either an edge or a player-placed tile
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
        layTrack: Tile * int * int
        Links a Tile that's being placed on the edge of the board to the appropriate OuterStations
            neighbor - the ConnectedTile that's being added on the edge of the board
            side - the ID of the correct OuterStations object
            station - the cable car station to which the link should be made *(0-31)*
            rememberTile - whether to retain the reference to this tile; alternative is to only tell the tile about us
        NOTE: At this level, the cable car station is represented using a 0-based indexing system; this contrasts with the 1-based scheme used at all levels higher!
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
        return self.rideTrack(track).tabulateScore(self._terminal(track))
    
    def followRoute(self, track):
        """
        followRoute: int -> tuple(Tile, int)
        Returns the tile to which this track connects and to which side of that tile it is linked
            track - the cable car station *(0-31)*
        NOTE: At this level, the cable car station is represented using a 0-based indexing system; this contrasts with the 1-based scheme used at all levels higher!
        """
        return self.rideTrack(track).followRoute(track/8)
    
    def reverseFollowRoute(self, tile, side):
        """
        reverseFollowRoute: Tile * int -> int
        Returns the cable car station *(0-31)* from which the track ending at the specified tile originates.  If the route doesn't touch any of these stations, the sentinel -1 is returned.
            tile - the ConnectedTile at the end of the track, or an empty Tile on the edge of the board
            side - the side of the next tile in the route (after the last one) to which the route connects (0-3)
        NOTE: At this level, the cable car station is represented using a 0-based indexing system; this contrasts with the 1-based scheme used at all levels higher!
        """
        if isinstance(tile, ConnectedTile): #follow this route back
            station, substation=tile.reverseFollowRoute(side)
            if isinstance(station, OuterStations): #this route actually touches the edge
                return self.stations.index(station)*8+substation
            else:
                return -1
        else: #we were given a blank tile on the edge of the board
            station=self.stations[side]
            for substation in range(8):
                if station.lookupSource(substation)==tile: #we found the substation connected to this tile
                    return side*8+substation
            return -1 #didn't find it

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
    
    def routeComplete(self, _, __=None):
        """
        routeComplete: any * any -> bool
        This helper method is used to determine whether each Tile represents the end of its track, and if so, it returns whether it represents an ending that leaves the track complete.  This default implementation always replies that the route is incomplete.
            _ - ignored (included for compatibility with child classes' implementations)
            __ - likewise
        """
        return False
    
    def tabulateScore(self, _, runningScore=0, __=None):
        """
        tabulateScore: any * int * any -> int
        This helper method is used to determine each track's total score.  This particular default always returns the running score without incrementing it.
            _ - ignored (included for compatibility with child classes' implementations)
            runningScore - the running score
            __ - also ignored
        """
        return runningScore
    
    def followRoute(self, entryPoint, _=None):
        """
        followRoute: int -> tuple(Tile, int)
        This helper method is used to fetch the tile at the end of a track, as well as the side of this tile on which the rest of the track is.  This default returns a reference to this tile.
            entryPoint - this side of this tile on which the track enters (0-3)
            _ - ignored (included for compatibility with child classes' implementations)
        """
        return self, entryPoint
    
    def reverseFollowRoute(self, _, __=None):
        """
        reverseFollowRoute: Tile -> tuple(Tile, int)
        This method returns the tile from which the route of which this tile is a member originates, as well as the position where the route is attached.  This default returns a reference to this tile and the sentinel -1.
            _ - ignored (included for compatibility with child classes' implementations)
            __ - also ignored
        """
        return self, -1
    
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
        self.borderedTiles=[None for _ in range(8)]
    
    def addTrack(self, neighbor, substation, rememberTile=True):
        """
        addTrack: Tile * int
        Adds a Tile that is being placed on this edge of the board
            neighbor - the ConnectedTile to be linked
            substation - the index of the station to which the tile should be linked (0-7)
            rememberTile - whether to retain the reference to this tile; alternative is to only tell the tile about us
        """
        if rememberTile:
            self.borderedTiles[substation]=neighbor #make this edge remember new tile
        
        if isinstance(neighbor, ConnectedTile):
            neighbor.addBorderingTile(self, self.rotation) #make new tile remember this edge
    
    def lookupSource(self, substation):
        """
        lookupSource: int -> Tile
        Returns the Tile at this station
            substation - the index of the station containing the desired tile (0-7)
        """
        return self.borderedTiles[substation]
    
    def routeComplete(self, _, __=None):
        """
        routeComplete: any -> bool
        This helper method is used to determine whether each Tile represents the end of its track, and if so, it returns whether it represents an ending that leaves the track complete.  This override always replies that the route is complete.
            _ - ignored (included for compatibility with sibling classes' implementations)
            __ - likewise
        """
        return True
    
    def reverseFollowRoute(self, caller, _=None):
        """
        reverseFollowRoute: Tile -> tuple(Tile, int)
        This method returns the tile from which the route of which this tile is a member originates, as well as the position where the route is attached.  This override returns this object and the substation to which the track is connected.
            caller - the tile connected to this terminal
            _ - ignored (included for compatibility with sibling classes' implementations)
        """
        return self, self.borderedTiles.index(caller)

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
    
    def routeComplete(self, _, __=None):
        """
        routeComplete: any -> bool
        This helper method is used to determine whether each Tile represents the end of its track, and if so, it returns whether it represents an ending that leaves the track complete.  This override always replies that the route is complete.
            _ - ignored (included for compatibility with sibling classes' implementations)
            __ - likewise
        """
        return True
    
    def tabulateScore(self, _, runningScore, __=None):
        """
        tabulateScore: any * int -> int
        This helper method is used to determine each track's total score.  This override always returns twice the running score in order to award the deserved 2x bonus.
            _ - ignored (included for compatibility with child classes' implementations)
            runningScore - the running score
            __ - likewise
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
        Fixes a specific instance's connections, accounting for both the tile's type and its rotation
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
        Links this tile with that lying on the specified side
            neighbor - the tile with which this one should be linked (a two-way link will only be created if this is a ConnectedTile)
            side - on which side of this tile neighbor is sitting (0-3)
            mutualConnection - whether to connect both ways iff neighbor is a ConnectedTile
        pre: neighbor is not in borderingTiles.
        """
        self.borderingTiles[side]=neighbor
        if mutualConnection and isinstance(neighbor, ConnectedTile):
            neighbor.borderingTiles[self.adjacentSide(side)]=self #make the connection mutual
    
    def _entryPoint(self, source):
        """
        _entryPoint: Tile -> int
        Calculates the side at which the tile source enters this one (0-3)
            source - the tile whose path is being followed
        pre: source is in borderingTiles.
        """
        return self.borderingTiles.index(source)
    
    def _exitPoint(self, entryPoint):
        """
        _exitPoint: (Tile or int) -> int
        Calculates the side from which the streetcar arriving from or at entryPoint will emerge (0-3).
            entryPoint - the neighboring tile or slot at which this tile has been entered (0-3)
        """
        if isinstance(entryPoint, Tile):
            return self.internalConnections[self._entryPoint(entryPoint)]
        else:
            return self.internalConnections[entryPoint]
    
    def adjacentSide(self, knownSide):
        """
        adjacentSide: int -> int
        Calculates which side of a bordering tile the specified side of this tile would touch
            knownSide - the side of this tile (0-3)
        """
        return (knownSide-2)%len(self.borderingTiles)
    
    def nextTileSide(self, previousTileSide):
        """
        nextTileSide: int -> int
        Calculates on which side of this tile the next tile in the route starting on previousTileSide is.
            previousTileSide - the starting side of this tile (0-3)
        """
        return self._exitPoint(previousTileSide)
    
    def neighborOnSide(self, side):
        """
        hasNeighborOnSide: int -> Tile
        Fetches the tile bordering the specified side of this one
            side - the side of this tile to check (0-3)
        """
        return self.borderingTiles[side]
    
    def lookupDestination(self, source):
        """
        lookupDestination: (Tile or int) -> Tile
        Determines to which other tile this tile's path will lead if one is to start from specified neighboring tile or side of this tile
            source - the neighboring tile from where wants to trace the path or side of this tile from where one wants to start (0-3)
        """
        return self.neighborOnSide(self._exitPoint(source))
    
    def _loopingInfinitely(self, caller, visited):
        """
        _loopingInfinitely: (Tile or int) * list(ConnectedTile) -> bool
        Determines whether a recursive function is looping infinitely along the same track
        """
        if not isinstance(caller, Tile):
            caller=self.neighborOnSide(caller)
        
        for index in range(len(visited)):
            if visited[index]==caller and index<len(visited)-1 and visited[index+1]==self: #this same leap has been made before in the same direction
                return True
        return False
    
    def routeComplete(self, caller, visited=[]):
        """
        routeComplete: (Tile or int) * list(ConnectedTile) -> bool
        This helper method is used to determine whether each Tile represents the end of its track, and if so, it returns whether it represents an ending that leaves the track complete.  This override always recurses to the destination Tile's implementation of this method and returns the result of that call.
            caller - a reference to the Tile that called this method or the side of this tile from where we entered (0-3)
        """
        if self._loopingInfinitely(caller, visited):
            return False
        else:
            return self.lookupDestination(caller).routeComplete(self.adjacentSide(self._exitPoint(caller)), visited+[self])
    
    def tabulateScore(self, caller, runningScore=0, visited=[]):
        """
        tabulateScore: (Tile or int) * int * list(ConnectedTile) -> int
        This helper method is used to determine each track's total score.  This override always recurses to the destination Tile's implementation of this method, incrementing the score by 1, and returns the result of that call.  An infinite loop in the route will cause a sentinel return value of -1.
            caller - a reference to the Tile that called this method or the side of this tile from where we entered (0-3)
            runningScore - the running score
        """
        if self._loopingInfinitely(caller, visited):
            return -1
        else:
            return self.lookupDestination(caller).tabulateScore(self.adjacentSide(self._exitPoint(caller)), runningScore+1, visited+[self])
    
    def followRoute(self, caller, visited=[]):
        """
        followRoute: (Tile or int) * list(ConnectedTile) -> tuple(Tile, int)
        This helper method is used to fetch the tile at the end of a track, as well as the side of this tile on which the rest of the track is.  This override recurses to the destination Tile's implementation and returns that method's result.  An infinite loop in the route will cause a sentinel side value of -1 to be returned.
            entryPoint - a reference to the Tile that called this method or the side of this tile on which the track enters (0-3)
        """
        if self._loopingInfinitely(caller, visited):
            return self, -1
        else:
            return self.lookupDestination(caller).followRoute(self.adjacentSide(self._exitPoint(caller)), visited+[self])
    
    def reverseFollowRoute(self, caller, visited=[]):
        """
        reverseFollowRoute: (Tile or int) * list(ConnectedTile) -> tuple(Tile, int)
        This method returns the tile from which the route of which this tile is a member originates, as well as the position where the route is attached.  An infinite loop in the route will cause a sentinel side value of -1 to be returned.
            caller - a reference to the *next* Tile in this route or the side of the *next* tile in the chain to which this one connects (0-3)
        """
        if self._loopingInfinitely(caller, visited):
            return self, -1
        elif isinstance(caller, Tile):
            trackSide=self.internalConnections.index(self._entryPoint(caller)) #the side of *this* tile where the *preceding* tile is connected
        else:
            trackSide=self.internalConnections.index(self.adjacentSide(caller)) #the side of *this* tile where the *preceding* tile is connected
        
        return self.neighborOnSide(trackSide).reverseFollowRoute(self, visited+[self])
    
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
