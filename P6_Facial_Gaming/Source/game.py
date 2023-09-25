from config import BOARD_SIZE

class TicTacToeGame:
  class PositionOutOfBoardException(Exception):
    def __init__(self, position):
      x, y = position
      super().__init__("Position ({}, {}) is out of the board with size {}.".format(x, y, BOARD_SIZE))
  class PositionTakenException(Exception):
    def __init__(self, position):
      x, y = position
      super().__init__("Position ({}, {}) is already taken.".format(x, y))
  class WrongPositionFormatException(Exception):
    def __init__(self, position):
      super().__init__("Position {} doesn't have the right format.".format(position))

  def __init__(self):
    self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

  def move(self, position, turn):
    if position is None or not type(position) is tuple or not len(position) == 2:
      raise TicTacToeGame.WrongPositionFormatException(position)
    x, y = position
    if type(x) is not int or type(y) is not int:
      raise TicTacToeGame.WrongPositionFormatException(position)
    if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE:
      raise TicTacToeGame.PositionOutOfBoardException(position)
    if self.board[x][y] != None:
      raise TicTacToeGame.PositionTakenException(position)
    self.board[x][y] = turn

  def get_win(self):
    # horizontal
    for i in range(BOARD_SIZE):
      win = self.board[i][0]
      for j in range(BOARD_SIZE):
        if self.board[i][j] != win:
          win = None
          break
      if win != None:
        return win
    # vertical
    for j in range(BOARD_SIZE):
      win = self.board[0][j]
      for i in range(BOARD_SIZE):
        if self.board[i][j] != win:
          win = None
          break
      if win != None:
        return win
    # diagonal
    win = self.board[0][0]
    for i in range(BOARD_SIZE):
      if self.board[i][i] != win:
        win = None
        break
    if win != None:
      return win
    # reverse diagonal
    win = self.board[0][BOARD_SIZE-1]
    for i in range(BOARD_SIZE):
      if self.board[i][BOARD_SIZE - 1 - i] != win:
        win = None
        break
    if win != None:
      return win

  def has_ended(self):
    if self.get_win() != None:
      return True
    for i in range(BOARD_SIZE):
      for j in range(BOARD_SIZE):
        if self.board[i][j] == None:
          return False
    return True