import tkinter as tk
from tkinter import messagebox, ttk
import random
import pickle
from collections import namedtuple

Card = namedtuple('Card', ['rank', 'suit'])

class Deck:
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    suits = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
    values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}

    def __init__(self, playerChooseNumDecks=1, deckPenetration=1):
        self.playerChooseNumDecks = playerChooseNumDecks
        self.deckPenetration = deckPenetration
        self.shuffle_deck()

    def shuffle_deck(self):
        self.cards = [Card(rank, suit) for rank in self.ranks for suit in self.suits] * self.playerChooseNumDecks
        random.shuffle(self.cards)
        print(f"Deck shuffled. Total cards: {len(self.cards)}")  # Debug print

    def draw_card(self):
        penetration_limit = int((self.playerChooseNumDecks * 52) * (1 - self.deckPenetration))
        print(f"Cards left: {len(self.cards)}, Penetration limit: {penetration_limit}")  # Debug print
        if len(self.cards) <= penetration_limit:
            self.shuffle_deck()
            messagebox.showinfo("Deck Reshuffled", "The deck was reshuffled at the penetration level.")
        return self.cards.pop() if self.cards else None
    
    def save_deck(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.cards, f)

    def load_deck(self, filename):
        with open(filename, 'rb') as f:
            self.cards = pickle.load(f)

class Hand:
    def __init__(self):
        self.hand = []

    def add_card(self, card):
        if card:
            self.hand.append(card)

    def get_value(self):
        value = sum(Deck.values[card.rank] for card in self.hand)
        numAces = sum(1 for card in self.hand if card.rank == 'Ace')
        while value > 21 and numAces:
            value -= 10
            numAces -= 1
        return value

    def can_split(self):
        return len(self.hand) == 2 and Deck.values[self.hand[0].rank] == Deck.values[self.hand[1].rank]

    def __str__(self):
        return ' , '.join(f"{card.rank} of {card.suit}" for card in self.hand) + f" ({self.get_value()})"

class SideBets:
    def __init__(self):
        self.insurance = False

    def buy_insurance(self, response):
        if response.lower() == 'y':
            self.insurance = True
            print("Insurance bought.")
        else:
            self.insurance = False
            print("No insurance bought.")

class GameSetup:
    def __init__(self):
        self.playerChooseNumDecks = 1
        self.deckPenetration = 0.75  # Default penetration level set to 75%
        self.playWithInsurance = False
        self.playWithSurrender = False
        self.dealerStandOnSoft17 = True
        self.initialBankroll = 1000
        self.payoutOdds = 1.5
        self.loadFile = None

class KingOfBlackjack:
    def __init__(self, setup, deck, root):
        self.setup = setup
        self.deck = deck
        self.root = root
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Helvetica', 12))
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TEntry', font=('Helvetica', 12))
        self.create_main_menu()

    def create_main_menu(self):
        self.clear_window()

        self.root.title("Blackjack Game - Main Menu")

        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        play_button = ttk.Button(main_frame, text="Play Blackjack", command=self.create_game_screen)
        play_button.pack(pady=10)

        settings_button = ttk.Button(main_frame, text="Settings", command=self.create_settings_screen)
        settings_button.pack(pady=10)

        exit_button = ttk.Button(main_frame, text="Exit", command=self.root.quit)
        exit_button.pack(pady=10)

    def create_game_screen(self):
        self.clear_window()

        game_frame = ttk.Frame(self.root, padding="20 20 20 20")
        game_frame.pack(fill=tk.BOTH, expand=True)

        self.bankroll_label = ttk.Label(game_frame, text=f"Bankroll: {self.setup.initialBankroll}")
        self.bankroll_label.pack(pady=10)

        self.bet_label = ttk.Label(game_frame, text="Enter your bet amount:")
        self.bet_label.pack()
        
        self.bet_entry = ttk.Entry(game_frame)
        self.bet_entry.pack()

        self.start_button = ttk.Button(game_frame, text="Start Game", command=self.start_game)
        self.start_button.pack(pady=10)

        self.player_hand_label = ttk.Label(game_frame, text="Player's Hand:")
        self.player_hand_label.pack(pady=10)

        self.dealer_hand_label = ttk.Label(game_frame, text="Dealer's Hand:")
        self.dealer_hand_label.pack(pady=10)

        button_frame = ttk.Frame(game_frame)
        button_frame.pack(pady=10)

        self.hit_button = ttk.Button(button_frame, text="Hit", command=self.hit)
        self.hit_button.pack(pady=5, side=tk.LEFT)

        self.stand_button = ttk.Button(button_frame, text="Stand", command=self.stand)
        self.stand_button.pack(pady=5, side=tk.LEFT)

        self.double_button = ttk.Button(button_frame, text="Double Down", command=self.double_down)
        self.double_button.pack(pady=5, side=tk.LEFT)

        self.surrender_button = ttk.Button(button_frame, text="Surrender", command=self.surrender)
        self.surrender_button.pack(pady=5, side=tk.LEFT)

        self.split_button = ttk.Button(button_frame, text="Split", command=self.split)
        self.split_button.pack(pady=5, side=tk.LEFT)

        self.main_menu_button = ttk.Button(game_frame, text="Main Menu", command=self.create_main_menu)
        self.main_menu_button.pack(pady=10)

    def create_settings_screen(self):
        self.clear_window()

        settings_frame = ttk.Frame(self.root, padding="20 20 20 20")
        settings_frame.pack(fill=tk.BOTH, expand=True)

        self.root.title("Blackjack Game - Settings")

        self.back_button = ttk.Button(settings_frame, text="Back to Main Menu", command=self.create_main_menu)
        self.back_button.pack(pady=10)

        self.decks_label = ttk.Label(settings_frame, text="Number of Decks:")
        self.decks_label.pack()
        self.decks_entry = ttk.Entry(settings_frame)
        self.decks_entry.pack()
        self.decks_entry.insert(0, str(self.setup.playerChooseNumDecks))

        self.penetration_label = ttk.Label(settings_frame, text="Deck Penetration:")
        self.penetration_label.pack()
        self.penetration_entry = ttk.Entry(settings_frame)
        self.penetration_entry.pack()
        self.penetration_entry.insert(0, str(self.setup.deckPenetration))

        self.bankroll_label = ttk.Label(settings_frame, text="Initial Bankroll:")
        self.bankroll_label.pack()
        self.bankroll_entry = ttk.Entry(settings_frame)
        self.bankroll_entry.pack()
        self.bankroll_entry.insert(0, str(self.setup.initialBankroll))

        self.odds_label = ttk.Label(settings_frame, text="Blackjack Payout Odds (e.g., 3:2):")
        self.odds_label.pack()
        self.odds_entry = ttk.Entry(settings_frame)
        self.odds_entry.pack()
        self.odds_entry.insert(0, f"{int(self.setup.payoutOdds * 2)}:2")

        self.insurance_var = tk.BooleanVar(value=self.setup.playWithInsurance)
        self.surrender_var = tk.BooleanVar(value=self.setup.playWithSurrender)
        self.soft17_var = tk.BooleanVar(value=self.setup.dealerStandOnSoft17)

        self.insurance_check = ttk.Checkbutton(settings_frame, text="Play with Insurance", variable=self.insurance_var)
        self.insurance_check.pack(pady=5)

        self.surrender_check = ttk.Checkbutton(settings_frame, text="Play with Surrender", variable=self.surrender_var)
        self.surrender_check.pack(pady=5)

        self.soft17_check = ttk.Checkbutton(settings_frame, text="Dealer Stands on Soft 17", variable=self.soft17_var)
        self.soft17_check.pack(pady=5)

        self.save_button = ttk.Button(settings_frame, text="Save Settings", command=self.save_settings)
        self.save_button.pack(pady=10)

    def save_settings(self):
        try:
            self.setup.playerChooseNumDecks = int(self.decks_entry.get())
            self.setup.deckPenetration = float(self.penetration_entry.get())
            self.setup.initialBankroll = float(self.bankroll_entry.get())
            odds = self.odds_entry.get().split(':')
            self.setup.payoutOdds = float(odds[0]) / float(odds[1])
            self.setup.playWithInsurance = self.insurance_var.get()
            self.setup.playWithSurrender = self.surrender_var.get()
            self.setup.dealerStandOnSoft17 = self.soft17_var.get()
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid settings.")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_game(self):
        try:
            bet = float(self.bet_entry.get())
            if bet > 0 and bet <= self.setup.initialBankroll:
                self.current_bet = bet
                self.setup.initialBankroll -= bet  # Subtract the bet from the bankroll
                self.bankroll_label.config(text=f"Bankroll: {self.setup.initialBankroll}")
                self.playerHands = [Hand()]
                self.dealerHand = Hand()
                self.playerSurrendered = False
                self.playerHands[0].add_card(self.deck.draw_card())
                self.dealerHand.add_card(self.deck.draw_card())
                self.playerHands[0].add_card(self.deck.draw_card())
                self.dealerHand.add_card(self.deck.draw_card())
                self.show_initial_hands()
            else:
                messagebox.showerror("Invalid Bet", "Bet amount is invalid or exceeds bankroll.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the bet amount.")

    def show_initial_hands(self):
        self.player_hand_label.config(text=f"Player's Hand: {self.playerHands[0]}")
        if len(self.dealerHand.hand) > 1:
            visible_card = self.dealerHand.hand[1]
            visible_value = Deck.values[visible_card.rank]
            self.dealer_hand_label.config(text=f"Dealer's Hand: {visible_card.rank} of {visible_card.suit} and Hidden ({visible_value})")
        else:
            self.dealer_hand_label.config(text="Dealer's Hand: ")

    def hit(self):
        self.playerHands[0].add_card(self.deck.draw_card())
        self.player_hand_label.config(text=f"Player's Hand: {self.playerHands[0]}")
        if self.playerHands[0].get_value() > 21:
            messagebox.showinfo("Busted", "You busted!")
            self.end_round()

    def stand(self):
        self.dealer_turn()
        self.determine_winner()

    def double_down(self):
        self.playerHands[0].add_card(self.deck.draw_card())
        self.player_hand_label.config(text=f"Player's Hand: {self.playerHands[0]}")
        self.current_bet *= 2
        if self.playerHands[0].get_value() > 21:
            messagebox.showinfo("Busted", "You busted!")
        self.stand()

    def surrender(self):
        self.setup.initialBankroll += self.current_bet / 2  # Reclaim half the bet
        self.bankroll_label.config(text=f"Bankroll: {self.setup.initialBankroll}")
        messagebox.showinfo("Surrendered", f"You surrendered and reclaimed half your bet of {self.current_bet / 2}.")
        self.end_round()

    def split(self):
        if self.playerHands[0].can_split():
            new_hand = Hand()
            new_hand.add_card(self.playerHands[0].hand.pop())
            self.playerHands[0].add_card(self.deck.draw_card())
            new_hand.add_card(self.deck.draw_card())
            self.playerHands.append(new_hand)
            self.show_initial_hands()
        else:
            messagebox.showerror("Invalid Split", "Cannot split the current hand.")

    def dealer_turn(self):
        while self.dealerHand.get_value() < 17 or (self.dealerHand.get_value() == 17 and not self.setup.dealerStandOnSoft17):
            self.dealerHand.add_card(self.deck.draw_card())
        self.dealer_hand_label.config(text=f"Dealer's Hand: {self.dealerHand}")

    def determine_winner(self):
        dealer_value = self.dealerHand.get_value()
        for i, hand in enumerate(self.playerHands):
            player_value = hand.get_value()
            result = f"Player's hand {i + 1}: {hand}\nDealer's hand: {self.dealerHand}\nBet amount: {self.current_bet}\n"
            if player_value > 21:
                result += f"You lose. You lost {self.current_bet}."
            elif dealer_value > 21 or player_value > dealer_value:
                winnings = self.current_bet * 2
                result += f"You win! You won {winnings}."
                self.setup.initialBankroll += winnings
            elif player_value < dealer_value:
                result += f"Dealer wins. You lost {self.current_bet}."
            else:
                result += f"It's a push. You get your bet back."
                self.setup.initialBankroll += self.current_bet
            messagebox.showinfo("Round Result", result)
        self.bankroll_label.config(text=f"Bankroll: {self.setup.initialBankroll}")
        if self.setup.initialBankroll <= 0:
            messagebox.showinfo("Game Over", "Your bankroll is 0. Returning to main menu.")
            self.create_main_menu()
        else:
            self.end_round()

    def end_round(self):
        if messagebox.askyesno("Play Again", "Do you want to play another round?"):
            self.create_game_screen()
        else:
            self.create_main_menu()

root = tk.Tk()
setup = GameSetup()
deck = Deck(int(setup.playerChooseNumDecks), float(setup.deckPenetration))
KingOfBlackjack(setup, deck, root)
root.mainloop()
