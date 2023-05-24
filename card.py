import pygame
#
# Class to represent a Poker card
# Values are represented from 2-14,
# with 11-14 being J, Q, K, A respectively.
#
class Card():
    #standard with and height of each card.
    WIDTH = 120
    HEIGHT = 168
    
    #holds all the card images.
    SPADES_IMG = []
    CLUBS_IMG = []
    DIAMONDS_IMG = []
    HEARTS_IMG = []
    
    #loads the card images into the arrays
    for i in range(2, 15):
        card_img = pygame.image.load('cards/' + str(i) + 'H' + '.png')
        card_img = pygame.transform.scale(card_img, (WIDTH, HEIGHT))
        HEARTS_IMG.append(card_img)
            
        card_img = pygame.image.load('cards/' + str(i) + 'D' + '.png')
        card_img = pygame.transform.scale(card_img, (WIDTH, HEIGHT))
        DIAMONDS_IMG.append(card_img)
            
        card_img = pygame.image.load('cards/' + str(i) + 'C' + '.png')
        card_img = pygame.transform.scale(card_img, (WIDTH, HEIGHT))
        CLUBS_IMG.append(card_img)
            
        card_img = pygame.image.load('cards/' + str(i) + 'S' + '.png')
        card_img = pygame.transform.scale(card_img, (WIDTH, HEIGHT))
        SPADES_IMG.append(card_img)
    
    
    #initializing function.
    def __init__(self, val, suit):
        self.val = val
        self.suit = suit
    
    #getter method for card value
    def getVal(self):
        return self.val
    
    #returns a string representation of card
    def __str__(self):
        return f'{self.val}{self.suit}'
    
    #returns a string representation of card
    def __repr__(self):
        return f'{self.val}{self.suit}'
    
    def valOfSuit(self):
        if (self.suit == 'H'):
            return 1
        if (self.suit == 'D'):
            return 2
        if (self.suit == 'C'):
            return 3
        if (self.suit == 'S'):
            return 4
    
    #returns a string representation of card
    def toString(self):
        return str(self.val) + self.suit
    
    #compares two cards, is not used.
    def __lt__(self, other):
        if (self.val == other.val):
            return self.valOfSuit() < other.valOfSuit()
        else:
            return self.val < other.val
    
    #returns the correct index of where the card image can be found.
    def image_index(self):
        return self.val - 2
    
    
        #gets the corresponding card image.
    def get_card_image(self):
        index = self.image_index()
        if (self.suit == 'H'):
            return Card.HEARTS_IMG[index]
        if (self.suit == 'D'):
            return Card.DIAMONDS_IMG[index]
        if (self.suit == 'C'):
            return Card.CLUBS_IMG[index]
        return Card.SPADES_IMG[index]
    
    
    
    
    
