import random  # Import the random module to shuffle the deck and draw random cards
#import pickle  # Import pickle for serializing and deserializing the deck state
from collections import namedtuple  # Import namedtuple to create a simple card structure

# Define a Card as a namedtuple with 'rank' and 'suit' fields
Card = namedtuple('Card', ['rank', 'suit'])

# Class to represent a deck of cards
class Deck:
    # Define the ranks and suits available in a deck of cards
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    suits = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
    # Define the values associated with each rank
    values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}

    def __init__(self, playerChooseNumDecks=1):
        # Create a list of cards for the specified number of decks
        self.cards = [Card(rank, suit) for rank in self.ranks for suit in self.suits] * playerChooseNumDecks
        # Shuffle the deck
        random.shuffle(self.cards)

    # Method to draw a card from the deck
    def draw_card(self):
        return self.cards.pop()

    # Method to save the deck state to a file
    #def save_deck(self, filename):
    #    with open(filename, 'wb') as f:
    #        pickle.dump(self.cards, f)

    # Method to load the deck state from a file
    #def load_deck(self, filename):
    #    with open(filename, 'rb') as f:
    #        self.cards = pickle.load(f)

# Class to represent a hand of cards
class Hand:
    def __init__(self):
        self.hand = []  # Initialize an empty hand

    def add_card(self, card):
        self.hand.append(card)  # Add a card to the hand

    def get_value(self):
        # Calculate the total value of the hand
        value = sum(Deck.values[card.rank] for card in self.hand)
        # Count the number of aces in the hand
        numAces = sum(1 for card in self.hand if card.rank == 'Ace')
        # Adjust the value of aces if the total value exceeds 21
        while value > 21 and numAces:
            value -= 10
            numAces -= 1
        return value

    def get_visible_value(self):
        # Calculate the value of visible cards only
        visible_cards = self.hand[1:]  # Exclude the first (hidden) card
        value = sum(Deck.values[card.rank] for card in visible_cards)
        numAces = sum(1 for card in visible_cards if card.rank == 'Ace')
        while value > 21 and numAces:
            value -= 10
            numAces -= 1
        return value

# Class to represent side bets
class SideBets:
    def __init__(self):
        self.insurance = False  # Initialize insurance flag

    def buy_insurance(self):
        response = input("Dealer's upcard is an Ace. Do you want to buy insurance? (y/n): ").lower()
        if response == 'y':
            self.insurance = True
            print("Insurance bought.")
        else:
            self.insurance = False
            print("No insurance bought.")

# Class to set up the game with user preferences
class GameSetup:
    def __init__(self):
        self.playerChooseNumDecks = self.get_number_of_decks()  # Number of decks to play with
        self.playWithInsurance = self.ask_play_with_insurance()  # Whether to play with insurance
        self.playWithSurrender = self.ask_play_with_surrender()  # Whether to play with surrender
        self.dealerStandOnSoft17 = self.ask_dealer_stand_on_soft_17()  # Dealer stands on soft 17
        self.loadFile = self.ask_load_file()  # File to load deck state from

    def get_number_of_decks(self):
        while True:
            try:
                playerChooseNumDecks = int(input("Enter the number of decks you want to play with: "))
                if 1 <= playerChooseNumDecks < 101:
                    print(f"You decided to play with {playerChooseNumDecks} decks of playing cards.")
                    return playerChooseNumDecks
                else:
                    print("Please enter an integer between 1 and 100.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    def ask_play_with_insurance(self):
        while True:
            response = input("Do you want to play with insurance? (y/n): ").lower()
            if response in ['y', 'n']:
                return response == 'y'
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    def ask_play_with_surrender(self):
        while True:
            response = input("Do you want to play with surrender? (y/n): ").lower()
            if response in ['y', 'n']:
                return response == 'y'
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    def ask_dealer_stand_on_soft_17(self):
        while True:
            response = input("Should the dealer be required to stand on a soft 17? (y/n): ").lower()
            if response in ['y', 'n']:
                return response == 'y'
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    def ask_load_file(self):
        if input("Do you want to load a deck state from a file? (y/n): ").lower() == 'y':
            return input("Enter the filename to load the deck state: ")
        return None

# Class to represent the blackjack game
class Blackjack:
    def __init__(self, setup):
        self.playWithInsurance = setup.playWithInsurance  # Whether to play with insurance
        self.playWithSurrender = setup.playWithSurrender  # Whether to play with surrender
        self.dealerStandOnSoft17 = setup.dealerStandOnSoft17  # Dealer stands on soft 17
        self.deck = Deck(setup.playerChooseNumDecks)  # Create a deck with specified number of decks
        if setup.loadFile:
            self.deck.load_deck(setup.loadFile)  # Load deck state from file if provided
        self.playerHand = Hand()  # Create a hand for the player
        self.dealerHand = Hand()  # Create a hand for the dealer
        self.sideBet = SideBets()  # Create a side bet object
        self.playerSurrendered = False  # Initialize surrender flag
        self.start_game()  # Start the game

    def start_game(self):
        self.playerHand.add_card(self.deck.draw_card())  # Deal one card to the player
        self.dealerHand.add_card(self.deck.draw_card())  # Deal one card to the dealer
        self.playerHand.add_card(self.deck.draw_card())  # Deal second card to the player
        self.dealerHand.add_card(self.deck.draw_card())  # Deal second card to the dealer
        self.show_initial_hands()  # Show the initial hands
        self.player_turn()  # Handle the player's turn
        self.dealer_turn()  # Handle the dealer's turn
        self.determine_winner()  # Determine the winner of the game

    def show_initial_hands(self):
        print(f"Player's hand: {self.playerHand.hand} (value: {self.playerHand.get_value()})")
        print(f"Dealer's hand: [{self.dealerHand.hand[1]}, Hidden] (value: {self.dealerHand.get_visible_value()})")
        
        if self.dealerHand.get_value() == 21:
            print(f"Dealer's hand: {self.dealerHand.hand} (value: {self.dealerHand.get_value()})")
            if self.playerHand.get_value() == 21:
                print("You and the Dealer have Blackjack. The round ends in a push.")
            else:
                print("The Dealer has Blackjack. You lose your bet.")
        elif self.playerHand.get_value() == 21:
            print("You have Blackjack. You Win!")
        
        if self.playWithInsurance and self.dealerHand.hand[1].rank == 'Ace':
            self.sideBet.buy_insurance()  # Check for insurance offer

    def player_turn(self):
        while True:
            action = 'h/s/d'
            if self.playWithSurrender:
                action += '/r'
            action = input(f"Do you want to hit, stand, double down{', or surrender' if self.playWithSurrender else ''}? ({action}): ").lower()

            if action == 'h':
                self.playerHand.add_card(self.deck.draw_card())  # Add a card to the player's hand
                print(f"Player's hand: {self.playerHand.hand} (value: {self.playerHand.get_value()})")
                if self.playerHand.get_value() > 21:
                    print("Player busts!")
                    return
            elif action == 's':
                print("Player stands.")
                break
            elif action == 'd':
                self.playerHand.add_card(self.deck.draw_card())  # Add a card to the player's hand
                print(f"Player's hand: {self.playerHand.hand} (value: {self.playerHand.get_value()})")
                print("Player doubles down.")
                break
            elif action == 'r' and self.playWithSurrender:
                print("Player surrenders.")
                self.playerSurrendered = True
                return
            else:
                print("Invalid input. Please enter 'h' to hit, 's' to stand, 'd' to double down" + (", or 'r' to surrender" if self.playWithSurrender else "") + ".")

    def dealer_turn(self):
        print(f"Dealer's initial hand: {self.dealerHand.hand} (value: {self.dealerHand.get_value()})")
        
        while True:
            dealer_value = self.dealerHand.get_value()
            if self.dealerStandOnSoft17 and dealer_value == 17 and any(card.rank == 'Ace' for card in self.dealerHand.hand):
                print("Dealer stands on soft 17.")
                break
            if dealer_value < 17:
                self.dealerHand.add_card(self.deck.draw_card())  # Add a card to the dealer's hand
                print(f"Dealer draws: {self.dealerHand.hand[-1]}")
                print(f"Dealer's hand: {self.dealerHand.hand} (value: {self.dealerHand.get_value()})")
            else:
                break
        
        if self.dealerHand.get_value() > 21:
            print("Dealer busts!")
        else:
            print(f"Dealer stands with: {self.dealerHand.hand} (value: {self.dealerHand.get_value()})")

    def determine_winner(self):
        if self.playerSurrendered:
            print("You surrendered. You reclaim half your bet.")
            return

        player_value = self.playerHand.get_value()
        dealer_value = self.dealerHand.get_value()

        if player_value > 21:
            print("Dealer wins.")
        elif dealer_value > 21 or player_value > dealer_value:
            print("You win!")
        elif player_value < dealer_value:
            print("Dealer wins.")
        else:
            print("Push.")

setup = GameSetup()  # Get the setup from the player
Blackjack(setup)  # Start the game