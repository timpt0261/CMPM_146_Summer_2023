import time
from game import TicTacToeGame
from config import BOARD_SIZE

class TicTacToeGUI:
  def __init__(self, player1, player2):
    self.players = [player1, player2]

  def visualize_board(self, board):
    for i in range(BOARD_SIZE):
      print('|', end='')
      for j in range(BOARD_SIZE):
        print('X|' if board[i][j] == 0 else 'O|' if board[i][j] == 1 else ' |', end='')
      print()

  def run(self):
    turn = 0
    game = TicTacToeGame()
    try_counter = 0
    while not game.has_ended():
      if try_counter >= 25:
        raise Exception('It seems like the player cannot generate a right move...')
      self.visualize_board(game.board)
      print('Turn: {}'.format('X' if turn == 0 else 'O'))
      move = self.players[turn].get_move(game.board)
      try:
        try_counter += 1
        game.move(move, turn)
        #clear_output(wait=True)
        print('Player {} took position {}.'.format('X' if turn == 0 else 'O', move))
        turn = 1 - turn
        try_counter = 0
      except (TicTacToeGame.PositionTakenException, TicTacToeGame.PositionOutOfBoardException, TicTacToeGame.WrongPositionFormatException) as e:
        #clear_output(wait=True)
        print(str(e))
      #time.sleep(1)
    win = game.get_win()
    self.visualize_board(game.board)
    if win is None:
      print('The game has ended in draw!')
    else:
      print('Player {} has won!'.format('X' if win == 0 else 'O'))