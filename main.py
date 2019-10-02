from typing import List, Dict


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

    def __repr__(self) -> str:
        # Useful in debugging. This will just print the nodes name when the 
        # class instance is printed
        return self.name

    def neighbors(self) -> List[Node]:
        """Neighbors of the current node.

        Args:
            None
        Returns:
            List of current nodes neightbor nodes
        """

        return [node for node in [self.north, self.east, self.south, self.west] if node]

    def isOccupied(self) -> bool:
        return True if self.piece else False

    def isEmpty(self) -> bool:
        return not self.isOccupied()


class Piece:
    """A players piece

    Attributes:
        player: Player who owns this piece
        node: The node that this piece sit on
    """

    def __init__(self, player: Player):
        self.player: Player = player
        self.node: Node = None


class Player:
    """Actions a player can take

    Attributes:
        name: Name of the player
        pieces: List of pieces in the players hand
        board: Current board the player is playing on
    """

    def __init__(self, name, board: Board):
        self.name: str = name
        self.pieces: List[Piece] = [Piece(self) for x in range(0,9)]
        self.board: Board = board
        
    def placePiece(self, location: str) -> bool:
        """Place a piece from the players hand on the board

        Args:
            location: location the player would like to place their piece
        Returns:
            True if the player was able to successfully place their piece on the
            board otherwise False
        """

        if self.pieces:
            piece = self.pieces.pop()
            return self.board.placePiece(piece, location)
        return False

    
class Board:
    """Creates a repesentation of Nine Mens Morris board and maintains its state
    
    Attributes:
        board: Dictionary of nodes that represents the board. key: Node name
    """

    def __init__(self):
        self.board: Dict[str, Node] = {}
        self.createBoard()

    def createBoard(self):
        """
        Creates the board nodes and the relationships between them. 
        TODO: Could be refactored into loop
        """
        nodeMap = {
            'a7': ['d7','a4'], 'd7': ['g7','d6'], 'g7': ['g4'],
            'b6': ['d6','b4'], 'd6': ['f6','d5'], 'f6': ['f4'],
            'c5': ['d5','c4'], 'd5': ['e5'], 'e5': ['e4'],
            'a4': ['b4','a1'], 'b4': ['c4','b2'], 'c4': ['c3'],
            'e4': ['f4','e3'], 'f4': ['g4','f2'], 'g4': ['g1'],
            'c3': ['d3'], 'd3': ['e3','d2'], 'b2': ['d2'],
            'd2': ['f2','d1'], 'a1': ['d1'], 'd1': ['g1']
        }

        def createNode(name, neighbors: List[str]):
            """
            Recursivly create the board nodes and stitch the nodes together maintaining each nodes
            forward and reverse relationships with each other.
            """
            node = None
            self.board[name] = Node(name)
            node = self.board[name]
            for neighbor in neighbors:
                if neighbor not in self.board:
                    createNode(neighbor, nodeMap.get(neighbor,[]))

                neigh_node = self.board[neighbor]
                if neighbor[1] == name[1]: #east/west
                    node.east = neigh_node
                    neigh_node.west = node
                else:
                    node.south = neigh_node #north/south
                    neigh_node.north = node

        for name, neighbors in nodeMap.items():
            if name not in self.board:
                createNode(name, neighbors) 

    def placePiece(self, piece, location):
        """Place a piece on the board

        Args:
            location: location to place the piece
        Returns:
            True if able to successfully place the piece on the board otherwise False
        """

        node = self.board[location]
        if node.isEmpty():
            piece.node = node
            node.piece = piece
            return True
        return False

def main():
    pass

if __name__ == '__main__':
    main()