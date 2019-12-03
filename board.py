from typing import List, Dict
import logging

log = logging.getLogger(__name__)


class Node:
    """A spot on the board.

    Attributes:
        name: canonical name of the node. a7, d3, g4, etc
        north, east, south, west: Neighbor nodes of the current node
        piece: current piece occupying the node
    """

    def __init__(self, name: str):
        self.name: str = name
        self.north: Node = None
        self.east: Node = None
        self.south: Node = None
        self.west: Node = None
        self.piece: Piece = None
        log.info("Node created: %s", str(self))

    def __repr__(self) -> str:
        # Useful in debugging. Prints the node name and piece
        #  when the class instance is printed
        return '%s %s' % (self.name, 'X' if self.is_occupied() else '') 

    def neighbors(self) -> List["Node"]:
        """Neighbors of the current node.

        Args:
            None
        Returns:
            List of current nodes neightbor nodes
        """

        return [node for node in [self.north, self.east, self.south, self.west] if node]

    def is_occupied(self) -> bool:
        return bool(self.piece)

    def is_empty(self) -> bool:
        return not self.is_occupied()


class Piece:
    """A players piece

    Attributes:
        id: ID of the piece 
        player: Player who owns this piece
        node: The node that this piece sit on
    """

    def __init__(self, id: int, player: "Player"):
        self.id = id
        self.player: Player = player
        self.node: Node = None
        log.info("Piece created: %s", str(self))

    def __repr__(self) -> str:
        # Useful in debugging. This will just print the Player and Node
        # location when the class instance is printed
        return "%s - %d @ %s" % (getattr(self.player, 'name', 'None'), self.id, getattr(self.node, 'name', 'None'))

    def is_placed(self):
        return bool(self.node)
        
class Player:
    """Actions a player can take

    Attributes:
        name: Name of the player
        board: Current board the player is playing on
        pieces: Dict of pieces in the players hand
    """

    def __init__(self, name, id, board: "Board"):
        self.name: str = name
        self.id: int = id
        self.board: "Board" = board
        self.pieces: Dict[int, Piece] = {x: Piece(x, self) for x in range(9)}
        log.info("Player created: %s", str(self))

    def __repr__(self) -> str:
        # Useful in debugging. This will just print the Player name
        # when the class instance is printed
        return self.name
        
    def place_piece(self, piece: Piece, location: str) -> bool:
        """Place a piece from the players hand on the board

        Args:
            location: location the player would like to place their piece
        Returns:
            True if the player was able to successfully place their piece on the
            board otherwise False
        """

        if self.pieces:
            if piece not in self.pieces.values():
                log.error("Piece cannot be placed. It is not in the players hand.")
                return False
            if self.board.place_piece(piece, location):
                del self.pieces[piece.id]
                return True
        log.error("Piece cannot be placed. There are no pieces in the players hand.")
        return False

    def valid_moves(self):
        """  documentation placeholder """
        moves = set()
        phase = self.get_phase()
        if phase == 1 or phase == 3:
            for node in self.board.get_nodes():
                if node.is_empty():
                    moves.add(node.name)
        elif phase == 2:
            for placed_piece in self.get_placed_pieces():
                node = placed_piece.node
                for neighbor_node in node.neighbors():
                    if neighbor_node.is_empty():
                        moves.add(neighbor_node.name)
        return moves

    def remove_piece(self, piece):
        # remove this players piece
        if piece.player is self:
            if (piece in self.get_placed_pieces() and 
                (piece in self.get_removable_pieces() or
                not self.get_removable_pieces())):
                return self.board.remove_piece(piece)
            else:
                log.info("Can not remove %s piece. Piece is part of a mill.", piece)
        return False
        

    def move_piece(self, piece: Piece, location: str):
        if piece.player is self:
            return self.board.move_piece(piece, location)
        return False
        
    def get_placed_pieces(self):
        placed = []
        for piece in self.board.get_pieces():
            if piece.player is self:
                placed.append(piece)
        return placed

    def get_mills(self):
        return [x for x in self.board.get_mills() if x.player is self]

    def get_removable_pieces(self):
        return list(set(self.get_placed_pieces()) - set(self.get_mills()))

    def get_phase(self):
        if self.pieces:
            return 1
        elif not self.pieces and len(self.get_placed_pieces()) > 3:
            return 2
        elif not self.pieces and len(self.get_placed_pieces()) <= 3:
            return 3

    def can_fly(self):
        return self.get_phase() == 3

    def can_move(self):
        return len(self.valid_moves()) > 0 

    
class Board:
    """Creates a repesentation of Nine Mens Morris board and maintains its state
    
    Attributes:
        board: Dictionary of nodes that represents the board. key: Node name
    """
    node_map = {
        'a7': ['d7','a4'], 'd7': ['g7','d6'], 'g7': ['g4'],
        'b6': ['d6','b4'], 'd6': ['f6','d5'], 'f6': ['f4'],
        'c5': ['d5','c4'], 'd5': ['e5'], 'e5': ['e4'],
        'a4': ['b4','a1'], 'b4': ['c4','b2'], 'c4': ['c3'],
        'e4': ['f4','e3'], 'f4': ['g4','f2'], 'g4': ['g1'],
        'c3': ['d3'], 'd3': ['e3','d2'], 'e3':[],
        'b2': ['d2'], 'd2': ['f2','d1'], 'f2':[],
        'a1': ['d1'], 'd1': ['g1'], 'g1': []
    }

    def __init__(self):
        self.board: Dict[str, Node] = self.create_board()

    def create_board(self):
        board: Dict[str, Node] = {}
        for name, neighbors in node_map.items():
            if name not in board:
                board[name] = Node(name)
            node = board[name]
            for neighbor in neighbors:
                if neighbor not in board:
                    board[neighbor] = Node(neighbor)
                neigh_node = board[neighbor]
                
                if neighbor[1] == name[1]: #east/west
                    node.east = neigh_node
                    neigh_node.west = node
                else:
                    node.south = neigh_node #north/south
                    neigh_node.north = node
        return board

    def place_piece(self, piece: Piece, location: str) -> bool:
        """Place a piece on the board

        Args:
            location: location to place the piece
        Returns:
            True if able to successfully place the piece on the board otherwise False
        """
        if location not in self.board:
            log.error("Piece cannot be placed. Invalid location: %s.", location)
            return False
        node = self.board[location]
        if node.is_empty():
            piece.node = node
            node.piece = piece
            log.info("Piece placed @ %s", location)
            return True
        log.info("Piece cannot be placed. Occupied by: %s.", str(node.piece))
        return False
        
    def remove_piece(self, piece: Piece):
        node = piece.node
        node.piece = None
        return True

    def move_piece(self, piece: Piece, location: str):
        node = piece.node
        if self.place_piece(piece, location):
            node.piece = None
            return True
        return False

    def get_pieces(self):
        pieces = []
        for node in self.board.values():
            if node.is_occupied():
                pieces.append(node.piece)
        return pieces

    def get_nodes(self):
        return list(self.board.values())

    def get_mills(self):
        def is_same_player(a, b, c):
            try:
                result = a.piece.player == b.piece.player and b.piece.player == c.piece.player
            except AttributeError:
                result = False
            return result
                
        mills = set()
        for curr in self.get_nodes():
            east = curr.east
            east_east = east.east if east else None

            west = curr.west
            west_west = west.west if west else None

            north = curr.north
            north_north = north.north if north else None
            
            south = curr.south
            south_south = south.south if south else None

            if (is_same_player(curr, east, east_east) or 
                is_same_player(curr, west, west_west) or 
                is_same_player(curr, east, west) or 
                is_same_player(curr, north, north_north) or 
                is_same_player(curr, south, south_south) or 
                is_same_player(curr, north, south)):
                mills.add(curr.piece)

        return mills


def main():
    pass

if __name__ == '__main__':
    log.info("Board imported")
    main()