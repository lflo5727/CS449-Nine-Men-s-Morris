import logging
import pygame
import pygame.gfxdraw

log = logging.getLogger(__name__)
pygame.init()

WIN_SIZE = (640, 480)
TILESIZE = 48
GRID_SIZE = 7
X_OFFSET = (WIN_SIZE[0] - TILESIZE * GRID_SIZE) // 2
Y_OFFSET = 120
Y_OFFSET_PLAYER = 70
RADIUS = 20

class Gui:
    class Line:
        def __init__(self, x1, y1, x2, y2):
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2

        def draw(self, surface):
            pygame.draw.line(surface, pygame.Color('#aaaaaa'), (self.x1, self.y1), (self.x2, self.y2), 5)

    class Circle:
        def __init__(self, x, y, color, outline = None, r = RADIUS):
            self.x = int(x)
            self.y = int(y)
            self.r = int(r)
            self.color = color
            self.outline = outline

        @property
        def v(self):
            return pygame.math.Vector2(self.x, self.y)

        @property
        def xy(self):
            return (self.x, self.y)

        def draw(self, surface):
            if self.outline:
                bg_circ_def = (surface, self.x, self.y, self.r, self.outline)
                pygame.gfxdraw.aacircle(*bg_circ_def)
                pygame.gfxdraw.filled_circle(*bg_circ_def)
            circ_def = (surface, self.x, self.y, (self.r - 2) if self.outline else self.r, self.color)
            pygame.gfxdraw.aacircle(*circ_def)
            pygame.gfxdraw.filled_circle(*circ_def)

        def distance_to(self, vector):
            return self.v.distance_to(vector)

        def move(self, x, y):
            self.x = int(x)
            self.y = int(y)


    class Node(Circle):
        def __init__(self, x, y, node):
            super().__init__(x, y, pygame.Color('#aaaaaa'), r = RADIUS - 1 )
            self.node = node
    
        def __repr__(self) -> str:
            return '[NODE] %s' % (self.node)

        def draw(self, surface):
            super().draw(surface)
            text = pygame.font.Font('assets/GameCube.ttf', 12).render(self.node.name, True, pygame.Color('#dddddd'))
            surface.blit(text, text.get_rect(center=self.v))

        def move(self, *args, **kwargs):
            log.error("Can not move a Node!")


    class Piece(Circle):
        def __init__(self, x, y, color, piece):
            super().__init__(x, y, color, outline = pygame.Color('#ffffff'))
            self.piece = piece

        def __repr__(self) -> str:
            return '[PIECE] %s' % (self.piece)


    class Board:
        def __init__(self, board):
            self.surface = pygame.Surface(WIN_SIZE)
            self.board = board
            self.nodes = None
            self.edges = None
            self.create()

        def create(self):
            def calc_node_center(node_name):
                col = ord(node_name[0]) - ord('a')
                row = 7 - int(node_name[1])
                x = col * TILESIZE + X_OFFSET + TILESIZE // 2
                y = row * TILESIZE + Y_OFFSET + TILESIZE // 2
                return (x, y)
            
            self.nodes = {}
            self.edges = []

            for node_name, node in self.board.items():
                x, y = calc_node_center(node_name)
                self.nodes[node_name] = Gui.Node(x, y, node)
                for neighbor in filter(lambda x: x is not None, [node.east, node.south]):
                    neighbor_x, neighbor_y = calc_node_center(neighbor.name)
                    self.edges.append(Gui.Line(x, y, neighbor_x, neighbor_y))
        
        def draw(self, screen):
            self.surface.fill(pygame.Color('#dddddd'))
            self.surface.blit(pygame.image.load('assets/background.png'), (0,0))

            font48 = pygame.font.Font('assets/GameCube.ttf', 48)
            
            title = font48.render("Nine men's morris", True, pygame.Color('#ffffff'))
            title_shadow = font48.render("Nine men's morris", True, pygame.Color('#7a8a9a'))
            
            self.surface.blit(title_shadow, title_shadow.get_rect(center=(WIN_SIZE[0]//2, 24)).move(2, 2))
            self.surface.blit(title, title.get_rect(center=(WIN_SIZE[0]//2, 24)))

            for edge in self.edges:
                edge.draw(self.surface)
                
            for node in self.nodes.values():
                node.draw(self.surface)

            screen.blit(self.surface, (0, 0))


    class Player:
        def __init__(self, id, player):
            self.id = id
            if self.id == 1:
                self.color =  pygame.Color('#E34996')
                self.placemat_degree = 90
                self.placemat_x_calc = lambda self, w: w // 2
            elif self.id == 2:
                self.color =  pygame.Color('#96E349')
                self.placemat_degree = 270
                self.placemat_x_calc = lambda self, w: WIN_SIZE[0] - w // 2

            self.player = player
            self.pieces = {}
            self.create()

        def create(self):
            if self.id == 1:
                x = X_OFFSET // 2
            elif self.id == 2:
                x = WIN_SIZE[0] - X_OFFSET // 2

            for piece_id, piece in self.player.pieces.items():
                y = piece_id * (RADIUS * 2 + 5) + Y_OFFSET_PLAYER + 5 + RADIUS // 2
                self.pieces[piece_id] = Gui.Piece(x, y, self.color, piece)

        def draw(self, screen):
            font48 = pygame.font.Font('assets/GameCube.ttf', 48)
            placemat = font48.render(self.player.name, True, pygame.Color('#cccccc'))
            placemat = pygame.transform.rotate(placemat, self.placemat_degree)
            screen.blit(placemat, placemat.get_rect(center=(self.placemat_x_calc(self, placemat.get_width()), WIN_SIZE[1] // 2 + Y_OFFSET_PLAYER // 2)))
            
            for piece in self.pieces.values():
                piece.draw(screen)
        

    def __init__(self, board, player1, player2):
        self.board = Gui.Board(board.board)
        self.players = {1: Gui.Player(1, player1), 2: Gui.Player(2, player2)}
        self.screen = pygame.display.set_mode(WIN_SIZE)

    def get_piece(self, vector):
        for player in self.players.values():
            for piece in player.pieces.values():
                if piece.distance_to(vector) <= RADIUS:
                    return piece

    def get_node(self, vector):
        for node in self.board.nodes.values():
            if node.distance_to(vector) <= RADIUS:
                return node

    def tell(self, vector):
        result = [self.get_node(vector), self.get_piece(vector)]
        return ', '.join([str(x) for x in result if x])

    def draw_board(self):
        self.board.draw(self.screen)

    def draw_pieces(self):
        for player in self.players.values():
            player.draw(self.screen)

    def game_message(self, *args):
        font = pygame.font.Font('assets/Monoid-Bold.ttf', 18)
        text = font.render(', '.join([m for m in args if m]), True, pygame.Color('#4996E3'))
        self.screen.blit(text, text.get_rect(center=(WIN_SIZE[0]//2, text.get_height()//2 + Y_OFFSET - text.get_height() * 2)))

    def debug_message(self, *args):
        font = pygame.font.Font('assets/Monoid-Regular.ttf', 12)
        text = font.render(', '.join([m for m in args if m]), True, pygame.Color('#aaaaaa'))
        self.screen.blit(text, text.get_rect(center=(WIN_SIZE[0]//2, WIN_SIZE[1] - text.get_height()//2)))
             

def main():
    pass

if __name__ == '__main__':
    main()