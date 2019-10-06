import random
import pygame
import pygame.gfxdraw

WIN_SIZE = (640, 480)
TILESIZE = 48
GRID_SIZE = 7
X_OFFSET = (WIN_SIZE[0] - TILESIZE * GRID_SIZE) // 2
Y_OFFSET = 120
Y_OFFSET_PLAYER = 70
RADIUS = 20


class Circle:
    def __init__(self, x_center, y_center, r, color, outline = None):
        self.x_center = x_center
        self.y_center = y_center
        self.r = r
        self.color = color
        self.outline = outline

    def draw(self, surface):
        if self.outline:
            bg_circ_def = (surface, self.x_center, self.y_center, self.r, self.outline)
            pygame.gfxdraw.aacircle(*bg_circ_def)
            pygame.gfxdraw.filled_circle(*bg_circ_def)
        circ_def = (surface, self.x_center, self.y_center, (self.r - 2) if self.outline else self.r, self.color)
        pygame.gfxdraw.aacircle(*circ_def)
        pygame.gfxdraw.filled_circle(*circ_def)
        

class Line:
    def __init__(self, x1, y1, x2, y2, width, color):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = width
        self.color = color

    def draw(self, surface):
        pygame.draw.line(surface, self.color, (self.x1, self.y1), (self.x2, self.y2), self.width)
        

class Gui:
    def __init__(self, board, player1, player2):
        self.board = board
        self.player1 = player1
        self.player1_grid = {}
        self.player2 = player2
        self.player2_grid = {}

        pygame.init()
        self.font12 = pygame.font.Font('GameCube.ttf', 12)
        self.font48 = pygame.font.Font('GameCube.ttf', 48)
        self.screen = pygame.display.set_mode(WIN_SIZE)
        self.board_surface = pygame.Surface(WIN_SIZE)
        
        self.board_grid = None
        self.board_lines = None
        self.create_board()
        self.create_players_pieces()

    def create_board(self):
        def calc_node_pos(node_name):
            col = ord(node_name[0]) - ord('a')
            row = 7 - int(node_name[1])
            return (col, row)

        def calc_node_center(col, row):
            col_center = col * TILESIZE + X_OFFSET + TILESIZE // 2
            row_center = row * TILESIZE + Y_OFFSET + TILESIZE // 2
            return (col_center, row_center)
        
        self.board_grid = {}
        self.board_lines = []

        for node_name, node in self.board.board.items():
            col, row = calc_node_pos(node_name)
            col_center, row_center = calc_node_center(col, row)
            for n in [node.east, node.south]:
                if n:
                    temp_node_name = n.name
                    temp_col, temp_row = calc_node_pos(temp_node_name)
                    temp_col_center, temp_row_center = calc_node_center(temp_col, temp_row)
                    self.board_lines.append(Line(col_center, row_center, temp_col_center, temp_row_center, 5, pygame.Color('#aaaaaa')))
            self.board_grid[node_name] = (col_center, row_center, node)
    
    def draw_board(self):
        self.board_surface.fill(pygame.Color('#dddddd'))

        p1_placemat = self.font48.render(self.player1.name, True, pygame.Color('#cccccc'))
        p1_placemat = pygame.transform.rotate(p1_placemat, 90)
        self.board_surface.blit(p1_placemat, p1_placemat.get_rect(center=(p1_placemat.get_width() // 2, WIN_SIZE[1] // 2 + Y_OFFSET_PLAYER // 2)))
        p2_placemat = self.font48.render(self.player2.name, True, pygame.Color('#cccccc'))
        p2_placemat = pygame.transform.rotate(p2_placemat, 270)
        self.board_surface.blit(p2_placemat, p2_placemat.get_rect(center=(WIN_SIZE[0] - p2_placemat.get_width() // 2, WIN_SIZE[1] // 2 + Y_OFFSET_PLAYER // 2)))

        title = self.font48.render("Nine men's morris", True, pygame.Color('#ffffff'))
        title_shadow = self.font48.render("Nine men's morris", True, pygame.Color('#7a8a9a'))
        self.board_surface.blit(title_shadow, title_shadow.get_rect(center=(WIN_SIZE[0]//2, 24)).move(1, 1))
        self.board_surface.blit(title, title.get_rect(center=(WIN_SIZE[0]//2, 24)))

        for line in self.board_lines:
            line.draw(self.board_surface)
        for name, grid_info in self.board_grid.items():
            centers = (grid_info[0], grid_info[1])
            circ = Circle(centers[0], centers[1], RADIUS - 1, pygame.Color('#aaaaaa'))
            text = self.font12.render(name, True, pygame.Color('#dddddd'))
            circ.draw(self.board_surface)
            self.board_surface.blit(text, text.get_rect(center=centers))

    def create_players_pieces(self):
        self.create_pieces(self.player1, self.player1_grid, 1)
        self.create_pieces(self.player2, self.player2_grid, 2)

    def create_pieces(self, player, player_grid, start_pos):
        col_center = X_OFFSET // 2
        if start_pos == 2:
            col_center = WIN_SIZE[0] - X_OFFSET // 2

        for i, piece in enumerate(player.pieces):
            row_center = i * (RADIUS * 2 + 5) + Y_OFFSET_PLAYER + 5 + RADIUS // 2
            player_grid[i] = (col_center, row_center, piece)

    def draw_player_pieces(self, player_grid, color):
        for _, piece_info in player_grid.items():
            col_center, row_center, _ = piece_info
            circ = Circle(col_center, row_center, RADIUS, color, pygame.Color('#ffffff'))
            circ.draw(self.screen)

    def get_player_piece_at_vector(self, player_grid, vector):
        for piece_id, piece_info in player_grid.items():
            col_center, row_center, piece = piece_info
            piece_pos = pygame.Vector2(col_center, row_center)
            if piece_pos.distance_to(vector) <= RADIUS:
                return piece_id

    def get_node_at_vector(self, vector):
        for node_name, node_info in self.board_grid.items():
            col_center, row_center, node = node_info
            node_pos = pygame.Vector2(col_center, row_center)
            if node_pos.distance_to(vector) <= RADIUS:
                return node_name

    def set_player_piece_xy(self, player_grid, piece_id, x, y):
        player_grid[piece_id] = (
            int(x),
            int(y),
            player_grid[piece_id][2]
        )

    def game_message(self, *args):
        font = pygame.font.Font('Monoid-Bold.ttf', 18)
        text = font.render(', '.join([m for m in args if m]), True, pygame.Color('#4996E3'))
        self.screen.blit(text, text.get_rect(center=(WIN_SIZE[0]//2, text.get_height()//2 + Y_OFFSET - text.get_height() * 2)))

    def debug_message(self, *args):
        font = pygame.font.Font('Monoid-Regular.ttf', 12)
        text = font.render(', '.join([m for m in args if m]), True, pygame.Color('#aaaaaa'))
        self.screen.blit(text, text.get_rect(center=(WIN_SIZE[0]//2, WIN_SIZE[1] - text.get_height()//2)))
            
    def hover_and_tell(self):
        # node < piece
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) 

        for player_grid in [self.player1_grid, self.player2_grid]:
            for piece_id, piece_info in player_grid.items():
                centers = (piece_info[0], piece_info[1])
                piece = piece_info[2]
                piece_pos = pygame.Vector2(centers)
                if piece_pos.distance_to(mouse_pos) <= RADIUS:
                    return "PIECE - [%s]%s" % (piece_id + 1, piece)

        for node_name, grid_info in self.board_grid.items():
            centers = (grid_info[0], grid_info[1])
            node_pos = pygame.Vector2(centers)
            if node_pos.distance_to(mouse_pos) <= RADIUS:
                return "NODE - %s" % (node_name)
        

def main():
    pass

if __name__ == '__main__':
    main()