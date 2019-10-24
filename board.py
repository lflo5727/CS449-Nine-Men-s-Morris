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
        return "%s - %d @ %s" % (self.player.name, self.id, self.node.name if self.node else "None")

    def is_placed(self):
        return bool(self.node)
        
class Player:
    """Actions a player can take

    Attributes:
        name: Name of the player
        board: Current board the player is playing on
        pieces: Dict of pieces in the players hand
    """

    def __init__(self, name, board: "Board"):
        self.name: str = name
        self.board: "Board" = board
        self.pieces: Dict[int, Piece] = {x: Piece(x, self) for x in range(9)}
        log.info("Player created: %s", str(self))

    def __repr__(self) -> str:
        # Useful in debugging. This will just print the Player name
        # when the class instance is printed
        return self.name
        
    def place_piece(self, piece_id: int, location: str) -> bool:
        """Place a piece from the players hand on the board

        Args:
            location: location the player would like to place their piece
        Returns:
            True if the player was able to successfully place their piece on the
            board otherwise False
        """

        if self.pieces:
            if piece_id not in self.pieces:
                log.error("Piece cannot be placed. It is not in the players hand.")
                return False
            if self.board.place_piece(self.pieces[piece_id], location):
                del self.pieces[piece_id]
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
            for node in self.board.get_nodes():
                if node.player is self:
                    for neighbor_node in node.neighbors():
                        if neighbor_node.is_empty():
                            moves.add(neighbor_node.name)
        return moves

    def remove_piece(self, piece):
        # remove this players piece
        if piece.player is self:
            self.board.remove_piece(piece)
        

    def move_piece(self, piece, location):

        pass

    def get_placed_pieces(self):
        placed = []
        for piece in self.board.get_pieces():
            if piece.player is self:
                placed.append(piece)
        return placed

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

    def __init__(self):
        self.board: Dict[str, Node] = {}
        self.create_board()

    def create_board(self):
        """Creates the board nodes and the relationships between them.
        """
        node_map = {
            'a7': ['d7','a4'], 'd7': ['g7','d6'], 'g7': ['g4'],
            'b6': ['d6','b4'], 'd6': ['f6','d5'], 'f6': ['f4'],
            'c5': ['d5','c4'], 'd5': ['e5'], 'e5': ['e4'],
            'a4': ['b4','a1'], 'b4': ['c4','b2'], 'c4': ['c3'],
            'e4': ['f4','e3'], 'f4': ['g4','f2'], 'g4': ['g1'],
            'c3': ['d3'], 'd3': ['e3','d2'], 'b2': ['d2'],
            'd2': ['f2','d1'], 'a1': ['d1'], 'd1': ['g1']
        }

        def create_node(name, neighbors: List[str]):
            """Recursivly create the board nodes and stitch the nodes together
            maintaining each nodes forward and reverse relationships with each other.
            """
            node = None
            self.board[name] = Node(name)
            node = self.board[name]
            for neighbor in neighbors:
                if neighbor not in self.board:
                    create_node(neighbor, node_map.get(neighbor,[]))

                neigh_node = self.board[neighbor]
                if neighbor[1] == name[1]: #east/west
                    node.east = neigh_node
                    neigh_node.west = node
                else:
                    node.south = neigh_node #north/south
                    neigh_node.north = node

        for name, neighbors in node_map.items():
            if name not in self.board:
                create_node(name, neighbors)
        log.info("Created board nodes")

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

    def move_piece(self):
        pass

    def get_pieces(self):
        pieces = []
        for node in self.board.values():
            if node.is_occupied():
                pieces.append(node.piece)
        return pieces

    def get_nodes(self):
        return list(self.board.values())

def main():
    pass

if __name__ == '__main__':
    log.info("Board imported")
    main()