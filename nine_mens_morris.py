import logging
import pygame

from board import Node, Piece, Board, Player
from gui import Gui

log = logging.getLogger("game_flow")
logging.basicConfig(level="INFO")

GAME_STATE = "STARTING"


def main():
    clock = pygame.time.Clock()

    board = Board()
    player1 = Player("Player 1", board)
    player2 = Player("Player 2", board)
    gui = Gui(board, player1, player2)
        
    selected_piece = None
    piece_prev_pos = None

    current_player = player1
    log.info("%s turn", current_player)

    GAME_STATE = "RUNNING"
    while True:
        events = pygame.event.get()
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) 
        
        for e in events:
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if selected_piece is None and (player1.pieces or player2.pieces):
                    selected_piece = gui.get_piece(mouse_pos)
                    if selected_piece is not None:
                        if selected_piece.piece.player is not current_player or selected_piece.piece.is_placed():
                            selected_piece = None
                        else:
                            log.info("Piece %s picked up.", selected_piece)
                            piece_prev_pos = selected_piece.xy
            if e.type == pygame.MOUSEBUTTONUP:
                if selected_piece is not None:
                    node = gui.get_node(mouse_pos)
                    if node is not None and current_player.place_piece(selected_piece.piece.id, node.node.name):
                        selected_piece.move(*node.xy)

                        if current_player is player1:
                            current_player = player2
                        else:
                            current_player = player1
                        log.info("%s turn", current_player)
                    else:
                        log.info("Piece cannot be placed. No node under mouse.")
                        x, y = piece_prev_pos
                        selected_piece.move(*piece_prev_pos)
                selected_piece = None

        gui.draw_board()
        if GAME_STATE == "RUNNING":
            if not player1.pieces and not player2.pieces:
                log.info("Game finished. No more pieces.")
                GAME_STATE = "CLOSED"
            else:
                gui.game_message("%s turn" % (current_player))
        else:
            gui.game_message("We're out of pieces!")
            
        if selected_piece is not None:
            selected_piece.move(*mouse_pos)
        gui.draw_pieces()
        gui.debug_message(str(mouse_pos), gui.tell(mouse_pos))
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()