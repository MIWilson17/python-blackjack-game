import random
#import pickle  # Import pickle for serializing and deserializing the deck state
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

    def draw_card(self):
        penetration_limit = int((self.playerChooseNumDecks * 52) - (self.deckPenetration * 52))
        if len(self.cards) < penetration_limit:
            print("Reshuffling the deck...")
            self.shuffle_deck()
        return self.cards.pop()
    
    # Method to save the deck state to a file
    #def save_deck(self, filename):
    #    with open(filename, 'wb') as f:
    #        pickle.dump(self.cards, f)

    # Method to load the deck state from a file
    #def load_deck(self, filename):
    #    with open(filename, 'rb') as f:
    #        self.cards = pickle.load(f)

class Hand:
    def __init__(self):
        self.hand = []

    def add_card(self, card):
        self.hand.append(card)

    def get_value(self):
        value = sum(Deck.values[card.rank] for card in self.hand)
        numAces = sum(1 for card in self.hand if card.rank == 'Ace')
        while value > 21 and numAces:
            value -= 10
            numAces -= 1
        return value

    def get_visible_value(self):
        visible_cards = self.hand[1:]
        value = sum(Deck.values[card.rank] for card in visible_cards)
        numAces = sum(1 for card in visible_cards if card.rank == 'Ace')
        while value > 21 and numAces:
            value -= 10
            numAces -= 1
        return value

    def __str__(self):
        return ' , '.join(f"{card.rank} of {card.suit}" for card in self.hand) + f" ({self.get_value()})"

class SideBets:
    def __init__(self):
        self.insurance = False

    def buy_insurance(self):
        response = input("Dealer's upcard is an Ace. Do you want to buy insurance? (y/n): ").lower()
        if response == 'y':
            self.insurance = True
            print("Insurance bought.")
        else:
            self.insurance = False
            print("No insurance bought.")

class GameSetup:
    def __init__(self):
        self.playerChooseNumDecks = self.get_number_of_decks()
        self.deckPenetration = self.get_deck_penetration(self.playerChooseNumDecks)
        self.playWithInsurance = self.ask_play_with_insurance()
        self.playWithSurrender = self.ask_play_with_surrender()
        self.dealerStandOnSoft17 = self.ask_dealer_stand_on_soft_17()
        self.loadFile = self.ask_load_file()

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

    def get_deck_penetration(self, num_decks):
        while True:
            try:
                deck_penetration = float(input(f"Enter the deck penetration level (up to {num_decks} decks): "))
                if 0 < deck_penetration <= num_decks:
                    print(f"You decided on a deck penetration of {deck_penetration} decks.")
                    return deck_penetration
                else:
                    print(f"Please enter a number between 0 and {num_decks}.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

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

class Blackjack:
    def __init__(self, setup, deck):
        self.playWithInsurance = setup.playWithInsurance
        self.playWithSurrender = setup.playWithSurrender
        self.dealerStandOnSoft17 = setup.dealerStandOnSoft17
        self.deck = Deck(setup.playerChooseNumDecks, setup.deckPenetration)
        self.deck = deck
        if setup.loadFile:
            self.deck.load_deck(setup.loadFile)
        self.playerHand = Hand()
        self.dealerHand = Hand()
        self.sideBet = SideBets()
        self.playerSurrendered = False
        self.start_game()

    def start_game(self):
        self.playerHand.add_card(self.deck.draw_card())
        self.dealerHand.add_card(self.deck.draw_card())
        self.playerHand.add_card(self.deck.draw_card())
        self.dealerHand.add_card(self.deck.draw_card())
        self.show_initial_hands()
        self.player_turn()
        self.dealer_turn()
        self.determine_winner()

    def show_initial_hands(self):
        print(f"Player's hand: {self.playerHand}")
        visible_card = self.dealerHand.hand[1]
        visible_value = Deck.values[visible_card.rank]
        print(f"Dealer's hand: {visible_card.rank} of {visible_card.suit} and Hidden (value: {visible_value})")
        
        if self.dealerHand.get_value() == 21:
            print(f"Dealer's hand: {self.dealerHand} (value: {self.dealerHand.get_value()})")
            if self.playerHand.get_value() == 21:
                print("You and the Dealer have Blackjack. The round ends in a push.")
            else:
                print("The Dealer has Blackjack. You lose your bet.")
        elif self.playerHand.get_value() == 21:
            print("You have Blackjack. You Win!")
        
        if self.playWithInsurance and self.dealerHand.hand[1].rank == 'Ace':
            self.sideBet.buy_insurance()

    def player_turn(self):
        while True:
            action = 'h/s/d'
            if self.playWithSurrender:
                action += '/r'
            action = input(f"Do you want to hit, stand, double down{', or surrender' if self.playWithSurrender else ''}? ({action}): ").lower()

            if action == 'h':
                self.playerHand.add_card(self.deck.draw_card())
                print(f"Player's hand: {self.playerHand}")
                if self.playerHand.get_value() > 21:
                    print("Player busts!")
                    return
            elif action == 's':
                print("Player stands.")
                break
            elif action == 'd':
                self.playerHand.add_card(self.deck.draw_card())
                print(f"Player's hand: {self.playerHand}")
                print("Player doubles down.")
                break
            elif action == 'r' and self.playWithSurrender:
                print("Player surrenders.")
                self.playerSurrendered = True
                return
            else:
                print("Invalid input. Please enter 'h' to hit, 's' to stand, 'd' to double down" + (", or 'r' to surrender" if self.playWithSurrender else "") + ".")

    def dealer_turn(self):
        print(f"Dealer's initial hand: {self.dealerHand}")
        
        while True:
            dealer_value = self.dealerHand.get_value()
            if self.dealerStandOnSoft17 and dealer_value == 17 and any(card.rank == 'Ace' for card in self.dealerHand.hand):
                print("Dealer stands on soft 17.")
                break
            if dealer_value < 17:
                self.dealerHand.add_card(self.deck.draw_card())
                print(f"Dealer draws: {self.dealerHand.hand[-1]}")
                print(f"Dealer's hand: {self.dealerHand}")
            else:
                break
        
        if self.dealerHand.get_value() > 21:
            print("Dealer busts!")
        else:
            print(f"Dealer stands with: {self.dealerHand}")

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

setup = GameSetup()
deck = Deck(setup.playerChooseNumDecks, setup.deckPenetration)
while True:
    Blackjack(setup, deck)
    response = input("Do you want to play another round? (y/n): ").lower()
    if response != 'y':
        print("Thank you for playing!")
        break