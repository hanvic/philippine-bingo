import random
import time
import os
from threading import Timer

class BingoGame:
    def __init__(self, num_players):
        self.num_players = num_players
        self.player_boards = []
        self.player_checked = []
        self.winning_pattern = None
        self.called_numbers = set()
        self.game_over = False

        for _ in range(num_players):
            self.player_boards.append(self.create_bingo_board())
            self.player_checked.append([[False]*5 for _ in range(5)])

        self.winning_pattern = self.create_winning_pattern()

    def create_bingo_board(self):
        numbers = list(range(1, 26))
        random.shuffle(numbers)
        return [numbers[i:i+5] for i in range(0, 25, 5)]

    def create_winning_pattern(self):
        pattern = [[False] * 5 for _ in range(5)]
        num_true = random.randint(8, 12)
        positions = [(i, j) for i in range(5) for j in range(5)]
        selected_positions = random.sample(positions, num_true)

        for i, j in selected_positions:
            pattern[i][j] = True
        return pattern

    def check_number(self, number):
        for player in range(self.num_players):
            for i in range(5):
                for j in range(5):
                    if self.player_boards[player][i][j] == number:
                        self.player_checked[player][i][j] = True

    def is_winner(self, player_idx):
        for i in range(5):
            for j in range(5):
                if self.winning_pattern[i][j] and not self.player_checked[player_idx][i][j]:
                    return False
        return True

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def draw_boards(self):
        self.clear_screen()
        # 승리 패턴 출력
        print("=== Winning Pattern ===")
        for row in self.winning_pattern:
            for cell in row:
                print("■  " if cell else "□  ", end="")
            print()
        print("\n")

        # 각 플레이어의 빙고판 출력
        for player in range(self.num_players):
            print(f"=== Player {player + 1}'s Board ===")
            for i in range(5):
                for j in range(5):
                    num = self.player_boards[player][i][j]
                    if self.player_checked[player][i][j]:
                        print(f"*{num:2d} ", end="")
                    else:
                        print(f" {num:2d} ", end="")
                print()
            print()

        print(f"Called Numbers: {sorted(list(self.called_numbers))}")

    def play_round(self):
        available_numbers = set(range(1, 26)) - self.called_numbers
        if not available_numbers:
            self.game_over = True
            return

        number = random.choice(list(available_numbers))
        print(f"\nCalling number: {number}")
        self.called_numbers.add(number)
        self.check_number(number)
        self.draw_boards()

        for player in range(self.num_players):
            if self.is_winner(player):
                print(f"\nPlayer {player + 1} wins!")
                self.game_over = True
                return

def play_game():
    num_players = int(input("Enter number of players: "))
    game = BingoGame(num_players)

    while not game.game_over:
        game.play_round()
        if not game.game_over:
            time.sleep(3)

if __name__ == "__main__":
    play_game()
