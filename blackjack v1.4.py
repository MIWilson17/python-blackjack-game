import random
import pickle  # Import pickle for serializing and deserializing the deck state
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
    def save_deck(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.cards, f)

    # Method to load the deck state from a file
    def load_deck(self, filename):
        with open(filename, 'rb') as f:
            self.cards = pickle.load(f)

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

    def can_split(self):
        return len(self.hand) == 2 and Deck.values[self.hand[0].rank] == Deck.values[self.hand[1].rank]

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
        self.initialBankroll = self.ask_initial_bankroll()
        self.payoutOdds = self.ask_payout_odds()
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

    def ask_initial_bankroll(self):
        while True:
            try:
                initialBankroll = float(input("Enter the initial bankroll amount: "))
                if initialBankroll > 0:
                    return initialBankroll
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def ask_payout_odds(self):
        while True:
            response = input("Choose your payout odds for Blackjack (2:1, 3:2, 6:5): ").lower()
            if response in ['2:1', '3:2', '6:5']:
                odds = response.split(':')
                return float(odds[0]) / float(odds[1])
            else:
                print("Invalid input. Please enter '2:1', '3:2', or '6:5'.")

    def ask_load_file(self):
        if input("Do you want to load a deck state from a file? (y/n): ").lower() == 'y':
            return input("Enter the filename to load the deck state: ")
        return None

class KingOfBlackjack:
    def __init__(self, setup, deck):
        self.playWithInsurance = setup.playWithInsurance
        self.playWithSurrender = setup.playWithSurrender
        self.dealerStandOnSoft17 = setup.dealerStandOnSoft17
        self.deck = Deck(setup.playerChooseNumDecks, setup.deckPenetration)
        self.deck = deck
        if setup.loadFile:
            self.deck.load_deck(setup.loadFile)
        self.playerHands = [Hand()]
        self.dealerHand = Hand()
        self.sideBet = SideBets()
        self.playerSurrendered = False
        self.bankroll = setup.initialBankroll
        self.payoutOdds = setup.payoutOdds
        self.start_game()

    def start_game(self):
        while True:
            print(f"\nCurrent bankroll: {self.bankroll}")
            bet = self.ask_for_bet()
            self.playerHands = [Hand()]
            self.dealerHand = Hand()
            self.playerSurrendered = False
            self.playerHands[0].add_card(self.deck.draw_card())
            self.dealerHand.add_card(self.deck.draw_card())
            self.playerHands[0].add_card(self.deck.draw_card())
            self.dealerHand.add_card(self.deck.draw_card())
            self.show_initial_hands(bet)
            self.player_turn(bet)
            if not self.playerSurrendered:  # Skip dealer turn if player surrenders
                self.dealer_turn()
            self.determine_winner(bet)
            if not self.ask_to_play_again():
                break

    def ask_for_bet(self):
        while True:
            try:
                bet = float(input("Enter your bet amount: "))
                if 0 < bet <= self.bankroll:
                    return bet
                else:
                    print(f"Invalid bet amount. Your current bankroll is {self.bankroll}.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def ask_to_play_again(self):
        response = input("Do you want to play another round? (y/n): ").lower()
        return response == 'y'

    def show_initial_hands(self, bet: float):
        print(f"Player's hand 1: {self.playerHands[0]}")
        visible_card = self.dealerHand.hand[1]
        visible_value = Deck.values[visible_card.rank]
        print(f"Dealer's hand: {visible_card.rank} of {visible_card.suit} and Hidden ({visible_value})")
        
        if self.dealerHand.get_value() == 21:
            print(f"Dealer's hand: {self.dealerHand} (21)")
            if self.playerHands[0].get_value() == 21:
                print("You and the Dealer have Blackjack. The round ends in a push.")
            else:
                print("The Dealer has Blackjack. You lose your bet.")
        elif self.playerHands[0].get_value() == 21:
            print("You have Blackjack. You Win!")
            self.bankroll += bet * self.payoutOdds
        
        if self.playWithInsurance and self.dealerHand.hand[1].rank == 'Ace':
            self.sideBet.buy_insurance()

    def player_turn(self, bet: float):
        i = 0
        while i < len(self.playerHands):
            hand = self.playerHands[i]
            while True:
                print(f"\nPlaying Player's hand {i + 1}: {hand}")
                action = 'h/s/d'
                if self.playWithSurrender:
                    action += '/r'
                if hand.can_split():
                    action += '/p'
                action = input(f"Do you want to hit, stand, double down{', or surrender' if self.playWithSurrender else ''}{', or split' if hand.can_split() else ''}? ({action}): ").lower()

                if action == 'h':
                    hand.add_card(self.deck.draw_card())
                    print(f"Player's hand {i + 1}: {hand}")
                    if hand.get_value() > 21:
                        print(f"Player's hand {i + 1} busts!")
                        break
                elif action == 's':
                    print(f"Player stands with hand {i + 1}.")
                    break
                elif action == 'd':
                    hand.add_card(self.deck.draw_card())
                    print(f"Player's hand {i + 1}: {hand}")
                    print(f"Player doubles down with hand {i + 1}.")
                    break
                elif action == 'r' and self.playWithSurrender:
                    print(f"Player surrenders hand {i + 1}.")
                    self.bankroll -= bet / 2
                    self.playerSurrendered = True
                    return
                elif action == 'p' and hand.can_split():
                    new_hand = Hand()
                    new_hand.add_card(hand.hand.pop())
                    hand.add_card(self.deck.draw_card())
                    new_hand.add_card(self.deck.draw_card())
                    self.playerHands.append(new_hand)
                    print(f"Player's hands: {[str(h) for h in self.playerHands]}")
                    i -= 1  # Adjust the index to revisit the split hand
                    break
                else:
                    print("Invalid input. Please enter 'h' to hit, 's' to stand, 'd' to double down" + (", or 'r' to surrender" if self.playWithSurrender else "") + (", or 'p' to split" if hand.can_split() else "") + ".")
            i += 1

    def dealer_turn(self):
        print(f"\nDealer's initial hand: {self.dealerHand}")
        
        while True:
            dealer_value = self.dealerHand.get_value()
            if self.dealerStandOnSoft17 and dealer_value == 17 and any(card.rank == 'Ace' for card in self.dealerHand.hand):
                print("Dealer stands on soft 17.")
                break
            if dealer_value < 17:
                drawn_card = self.deck.draw_card()
                self.dealerHand.add_card(drawn_card)
                print(f"Dealer draws: {drawn_card.rank} of {drawn_card.suit}")
                print(f"Dealer's hand: {self.dealerHand}")
            else:
                break
        
        if self.dealerHand.get_value() > 21:
            print("Dealer busts!")
        else:
            print(f"Dealer stands with: {self.dealerHand}")

    def determine_winner(self, bet: float):
        if self.playerSurrendered:
            print("You surrendered. You reclaim half your bet.")
            self.bankroll -= bet / 2  # Deduct half the bet from the bankroll
            return

        dealer_value = self.dealerHand.get_value()

        for i, hand in enumerate(self.playerHands):
            player_value = hand.get_value()
            print(f"\nPlayer's hand {i + 1}: {hand}")

            if player_value > 21:
                print(f"Dealer wins against Player's hand {i + 1}.")
                self.bankroll -= bet
            elif dealer_value > 21 or player_value > dealer_value:
                print(f"Player's hand {i + 1} wins!")
                self.bankroll += bet
            elif player_value < dealer_value:
                print(f"Dealer wins against Player's hand {i + 1}.")
                self.bankroll -= bet
            else:
                print(f"Player's hand {i + 1} pushes with the dealer.")

setup = GameSetup()
deck = Deck(setup.playerChooseNumDecks, setup.deckPenetration)
KingOfBlackjack(setup, deck)