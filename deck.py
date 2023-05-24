import random
from card import Card
import pygame

#
# Class to represent a Deck full of Card Objects.
#
class Deck():
    pygame.mixer.init()
    
    #initializes Deck object.
    def __init__(self):
        self.cards = []
        self.addCards()
    
    #adds all 52 cards to deck.
    def addCards(self):
        
        for i in range(2, 15):
            self.cards.append(Card(i, "S"))
            self.cards.append(Card(i, "C"))
            self.cards.append(Card(i, "H"))
            self.cards.append(Card(i, "D"))
    
    #shuffles the deck.
    def shuffle(self):
        for i in range(0, 1000):
            loc1 = random.randint(0, 51)
            loc2 = random.randint(0, 51)
            c1 = self.cards[loc1]
            self.cards[loc1] = self.cards[loc2]
            self.cards[loc2] = c1
    
    #prints a string representation of deck (for testing)
    def toString(self):
        for i in range(0, len(self.cards)):
            print(self.cards[i].toString())
    
    #removes top card from deck.     
    def removeCard(self):
        return self.cards.pop(0)
    
    #deals the initial flop.
    def dealFlop(self):
        flop = []
        self.cards.pop(0)
        flop.append(self.cards.pop(0))
        flop.append(self.cards.pop(0))
        flop.append(self.cards.pop(0))
        return flop
    
    #deals the turn.  
    def dealTurn(self):
        self.cards.pop(0)
        return self.cards.pop(0)
    
    #deals the river.
    def dealRiver(self):
        return self.dealTurn()
    
    #deals all the middle shared cards.
    def dealSharedCards(self):
        shared_cards = self.dealFlop()
        shared_cards.append(self.dealTurn())
        shared_cards.append(self.dealRiver())
        return shared_cards
    
    #deals the entire poker round.
    def dealPokerRound(self, players, dealerIndex):
        self.dealCards(players, dealerIndex)
        return self.dealSharedCards()
    
    #deals the cards to each player.
    def dealCards(self, players, dealerIndex):
        
        curPlayer = players[(dealerIndex + 1) % len(players)] #small blind
        dealerIndex += 1
        
        # deals first card to each player.
        for i in range(0, len(players)):
            #skips players if folded.
            while (curPlayer.folded):
                dealerIndex += 1
                curPlayer = players[(dealerIndex) % len(players)]
            
            #gives card to player
            curPlayer.hand[0] = self.removeCard()
            curPlayer = players[(dealerIndex + 1) % len(players)]
            dealerIndex += 1
            sound = pygame.mixer.Sound('sounds/flipcard.mp3')
            sound.play()
            pygame.time.delay(500)
        #deals second card to each player
        for i in range(0, len(players)):
            #skips players if folded.
            while (curPlayer.folded):
                dealerIndex += 1
                curPlayer = players[(dealerIndex) % len(players)]
            
            #gives card to player.
            curPlayer.hand[1] = self.removeCard()
            curPlayer = players[(dealerIndex + 1) % len(players)]
            dealerIndex += 1
            sound = pygame.mixer.Sound('sounds/flipcard.mp3')
            sound.play()
            pygame.time.delay(500)
        
        
        
        
            
                    