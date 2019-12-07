import logging
import pygame
import itertools

from board import Node, Piece, Board, Player, Phase, MAX_NUM_PIECES, MIN_NUM_PIECES
from ai_player import AI_Player
from gui import Gui

log = logging.getLogger("game_flow")
logging.basicConfig(level="INFO")

GAME_STATE = "STARTING"

def main():
    clock = pygame.time.Clock()

    board = Board()
    player1 = Player("Player 1", 1, board)
    player2 = AI_Player("Computer", 2, board, player1)
    #player2 = Player("Player 2", 2, board)
    gui = Gui(board, player1, player2)
    
   
    player_toggle = itertools.cycle([player1, player2])   
    current_player = next(player_toggle)

    selected_piece = None
    prev_selected_piece = None
    prev_selected_piece_pos = None
    can_remove_piece = False

    game_won_by = None
    while True:

        if isinstance(current_player, AI_Player):
            move = current_player.get_best_move()
            if move.phase == Phase.PLACING:
                piece = list(current_player.pieces.values())[0] 
                if current_player.place_piece(piece, move.dest):
                    node = gui.find_node(board.board[move.dest])
                    gui.find_piece(piece).move(*node.xy)
                else:
                    log.critical("AI BROKE. COULD NOT PLACE.")
            else:
                piece = board.board[move.src].piece
                if current_player.move_piece(piece, move.dest):
                    node = gui.find_node(board.board[move.dest])
                    gui.find_piece(piece).move(*node.xy)

            if move.remove:
                other_player = next(player_toggle)
                piece = board.board[move.remove].piece
                if other_player.remove_piece(piece):
                    for player in gui.players.values():
                        if player.player is piece.player:
                            player.remove_piece(piece.id)
                    log.info("Remove %s piece", piece)
                next(player_toggle) # skip the next cycle to return to normal

        events = pygame.event.get()
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) 
        
        for e in events:
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.MOUSEBUTTONDOWN:
                selected_piece = gui.get_piece(mouse_pos)
                if selected_piece:
                    log.info("%s piece picked up", selected_piece)
                    prev_selected_piece_pos = selected_piece.xy
            if e.type == pygame.MOUSEBUTTONUP:
                log.info("%s piece dropped", selected_piece)
                prev_selected_piece = selected_piece
                selected_piece = None

        if game_won_by:
            pass
        if selected_piece and not can_remove_piece:
            selected_piece.move(*mouse_pos)
        elif prev_selected_piece:
            action_succesful = False
            node = gui.get_node(mouse_pos)

            if can_remove_piece:
                other_player = next(player_toggle)
                if other_player.remove_piece(prev_selected_piece.piece):
                    for player in gui.players.values():
                        if player.player is prev_selected_piece.piece.player:
                            player.remove_piece(prev_selected_piece.piece.id)
                    log.info("Remove %s piece", prev_selected_piece.piece)
                    action_succesful = True
                    can_remove_piece = False
                next(player_toggle) # skip the next cycle to return to normal
            elif node:
                log.info("Over %s node", node)
                
                if current_player.get_phase() == Phase.PLACING:
                    if current_player.place_piece(prev_selected_piece.piece, node.node.name):
                        prev_selected_piece.move(*node.xy)
                        action_succesful = True
                else:
                    if node.node in prev_selected_piece.piece.node.neighbors() or current_player.can_fly():
                        if current_player.move_piece(prev_selected_piece.piece, node.node.name):
                            prev_selected_piece.move(*node.xy)
                            action_succesful = True
                    else:
                        log.info("Could move %s piece to %s node. Not a neighbor", prev_selected_piece, node)


            if not action_succesful:
                prev_selected_piece.move(*prev_selected_piece_pos)
            else:
                if prev_selected_piece.piece in current_player.get_mills():
                    can_remove_piece = True
                else:
                    current_player = next(player_toggle)
            prev_selected_piece = None
        
        
        if not player1.can_move() or not player1.pieces and len(player1.get_placed_pieces()) < MIN_NUM_PIECES:
            game_won_by = player2
        elif not player2.can_move() or not player1.pieces and len(player2.get_placed_pieces()) < MIN_NUM_PIECES:
            game_won_by = player1

        gui.draw_board()
        if game_won_by:
            gui.game_message("%s WON!" % (game_won_by))
        elif not can_remove_piece:
            gui.game_message("%s turn" % (current_player))
        else:
            gui.game_message("%s remove piece from other player." % (current_player))

        gui.draw_pieces()
        gui.debug_message(str(mouse_pos), gui.tell(mouse_pos))
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()