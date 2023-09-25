from gui import TicTacToeGUI
from player import RandomPlayer, UserInputPlayer, UserWebcamPlayer

if __name__ == '__main__':
    TicTacToeGUI(RandomPlayer(), UserWebcamPlayer()).run()