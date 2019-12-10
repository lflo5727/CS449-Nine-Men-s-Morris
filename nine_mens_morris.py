import logging
import pygame
import itertools

from board import Node, Piece, Board, Player, Phase, MAX_NUM_PIECES, MIN_NUM_PIECES
from ai_player import AI_Player
from gui import Gui, Choice, WIN_SIZE

log = logging.getLogger("game_flow")
logging.basicConfig(level="INFO")


def start_game():
    clock = pygame.time.Clock()
    board = Board()
    turns = 0
    MAX_TURNS = 500

    play_ai = None
    choice = Choice("Human", "Computer")
    choice.fade_in_sec = 6.5
    screen = pygame.display.set_mode(WIN_SIZE)
    while play_ai is None:
        events = pygame.event.get()
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) 
        
        for e in events:
            if e.type == pygame.QUIT:
                return 0
            if e.type == pygame.MOUSEBUTTONDOWN:
                if play_ai is None:
                    picked = choice.is_clicked(mouse_pos)
                    if picked == 1:
                        play_ai = False
                        player1 = Player("Player 1", 1, board)
                        player2 = Player("Player 2", 2, board)
                    elif picked == 2:
                        play_ai = True
                        player1 = Player("Player 1", 1, board)
                        player2 = AI_Player("Computer", 2, board, player1)
                    elif pygame.Rect(0,0,10,10).collidepoint(mouse_pos):
                        play_ai = "yes"
                        player1 = AI_Player("C3PO", 1, board, None)
                        player2 = AI_Player("R2D2", 2, board, player1)
                        player1.opponent = player2
        choice.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    gui = Gui(board, player1, player2)
    player_toggle = itertools.cycle([player1, player2])   
    current_player = next(player_toggle)

    selected_piece = None
    prev_selected_piece = None
    prev_selected_piece_pos = None
    can_remove_piece = False

    game_won_by = None
    while True:
        if isinstance(current_player, AI_Player) and not game_won_by:
            if current_player.get_phase() == Phase.FLYING:
                AI_Player.DEPTH = 3
            move = current_player.get_best_move()
            log.info("Move score: %d", move.score)
            if move.phase == Phase.PLACING:
                piece = list(current_player.pieces.values())[0] 
                if current_player.place_piece(piece, move.dest):
                    node = gui.find_node(board.board[move.dest])
                    gui.find_piece(piece).move(*node.xy)
                    log.info("Placed %s", piece)
                else:
                    log.critical("AI BROKE. COULD NOT PLACE.")
            else:
                piece = board.board[move.src].piece
                if current_player.move_piece(piece, move.dest):
                    node = gui.find_node(board.board[move.dest])
                    gui.find_piece(piece).move(*node.xy)
                    log.info("Moved %s piece from %s", piece, move.src)
                else:
                    log.critical("AI BROKE. COULD NOT MOVE.")

            if move.remove:
                other_player = next(player_toggle)
                piece = board.board[move.remove].piece
                if other_player.remove_piece(piece):
                    for player in gui.players.values():
                        if player.player is piece.player:
                            player.remove_piece(piece.id)
                    log.info("Computer removed %s piece", piece)
                else:
                    log.critical("AI BROKE. COULD NOT REMOVE.")
                next(player_toggle) # skip the next cycle to return to normal
            turns += 1
            current_player = next(player_toggle)

        events = pygame.event.get()
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) 
        mouse_btns = pygame.mouse.get_pressed()
        
        for e in events:
            if e.type == pygame.QUIT:
                return 0
            if e.type == pygame.MOUSEBUTTONDOWN and mouse_btns == (1,0,0):
                selected_piece = gui.get_piece(mouse_pos)
                if selected_piece:
                    log.info("%s piece picked up", selected_piece)
                    prev_selected_piece_pos = selected_piece.xy
            if e.type == pygame.MOUSEBUTTONUP and (mouse_btns == (0,0,0) or mouse_btns == (0,0,1)):
                log.info("%s piece dropped", selected_piece)
                prev_selected_piece = selected_piece
                selected_piece = None

        if game_won_by:
            pass
        elif selected_piece and not can_remove_piece:
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
        
        
        if turns >= MAX_TURNS or \
           not player1.can_move() and not player2.can_move() and \
           not player1.pieces and len(player1.get_placed_pieces()) < MIN_NUM_PIECES and \
           not player2.pieces and len(player2.get_placed_pieces()) < MIN_NUM_PIECES:
            game_won_by = "TIE! Everyone"
        elif not player1.can_move() or not player1.pieces and len(player1.get_placed_pieces()) < MIN_NUM_PIECES:
            game_won_by = player2
        elif not player2.can_move() or not player2.pieces and len(player2.get_placed_pieces()) < MIN_NUM_PIECES:
            game_won_by = player1

        gui.draw_board()
        if game_won_by:
            gui.game_message("%s WON!" % (game_won_by))
        elif not can_remove_piece:
            gui.game_message("%s turn" % (current_player))
        else:
            gui.game_message("%s remove piece from other player." % (current_player))

        choice = Choice("Quit", "Play new game")
        while game_won_by is not None:
            events = pygame.event.get()
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) 
            
            for e in events:
                if e.type == pygame.QUIT:
                    return 0
                if e.type == pygame.MOUSEBUTTONDOWN:
                    picked = choice.is_clicked(mouse_pos)
                    if picked == 1:
                        return 0
                    elif picked == 2:
                        return 1
            gui.draw_board()
            gui.game_message("%s WON!" % (game_won_by))
            gui.draw_pieces()

            gui.debug_message(str(turns), str(mouse_pos), gui.tell(mouse_pos))
            choice.draw(screen)
            pygame.display.flip()
            clock.tick(60)

        gui.draw_pieces()
        gui.debug_message(str(turns), str(mouse_pos), gui.tell(mouse_pos))
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    while start_game():
        pass
