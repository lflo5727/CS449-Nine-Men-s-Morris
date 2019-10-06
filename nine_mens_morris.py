import random
import itertools
import pygame

from board import Node, Piece, Board, Player
from gui import Gui

def main():
    clock = pygame.time.Clock()

    board = Board()
    player1 = Player("Player 1", board)
    player2 = Player("Player 2", board)
    gui = Gui(board, player1, player2)
        
    selected_piece = None
    piece_prev_pos = None

    current_player = gui.player1
    current_player_grid = gui.player1_grid
    while True:
        events = pygame.event.get()
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) 
        
        for e in events:
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if selected_piece is None and (player1.pieces or player2.pieces):
                    selected_piece = gui.get_player_piece_at_vector(current_player_grid, mouse_pos)
                    if selected_piece is not None:
                        if current_player_grid[selected_piece][2].node is not None:
                            selected_piece = None
                        else:
                            piece_prev_pos = (current_player_grid[selected_piece][0], current_player_grid[selected_piece][1])
            if e.type == pygame.MOUSEBUTTONUP:
                if selected_piece is not None:
                    node_name = gui.get_node_at_vector(mouse_pos)
                    if node_name is not None and current_player.place_piece(current_player_grid[selected_piece][2], node_name):
                        x, y, _ = gui.board_grid[node_name]
                        gui.set_player_piece_xy(current_player_grid, selected_piece, x, y)

                        if current_player is gui.player1:
                            current_player = gui.player2
                            current_player_grid = gui.player2_grid
                        else:
                            current_player = gui.player1
                            current_player_grid = gui.player1_grid
                    else:
                        x, y = piece_prev_pos
                        gui.set_player_piece_xy(current_player_grid, selected_piece, x, y)
                        
                selected_piece = None

        gui.screen.fill(pygame.Color('#dddddd'))
        gui.screen.blit(gui.board_surface, (0, 0))
        gui.draw_board()
        if(not player1.pieces and not player2.pieces):
            gui.game_message("We're out of pieces!")
        else:
            gui.game_message("%s TURN" % (current_player))
        
        if selected_piece is not None:
            gui.set_player_piece_xy(current_player_grid, selected_piece, mouse_pos.x, mouse_pos.y)
        gui.draw_player_pieces(gui.player1_grid, pygame.Color('#E34996'))
        gui.draw_player_pieces(gui.player2_grid, pygame.Color('#96E349'))
        gui.debug_message(str(pygame.mouse.get_pos()), gui.hover_and_tell())
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()