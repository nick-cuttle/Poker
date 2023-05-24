import pygame

#
# Class to represent a poker player
#
class Player():
    
    #width and height of every player.
    WIDTH = 250
    HEIGHT = 75
    
    #initialize a new player object.
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name
        self.color = (0, 0, 0)
        self.rect = (self.x, self.y, self.WIDTH, self.HEIGHT)
        self.hand = [None, None]
        self.money = 100
        self.isBig = False
        self.isSmall = False
        self.isDealer = False
        self.isTurn = False
        self.folded = False
        self.in_game = True
        self.bet = -1 # -1 denotes hasn't bet yet.
        self.total_win = 0 # amount of money won.
        self.index = 0
        self.win = False
        self.evaluation = ""
        
    #string representation of player.
    def __repr__(self):
        return f'{self.name}:{self.money}'
    
    #string representation of player.
    def __str__(self):
        return f'{self.name}:{self.money}'
    
    #draws the player to the screen
    def draw(self, win, pos):
        surface = pygame.Surface((self.WIDTH, self.HEIGHT))
        
        if (self.folded):
            surface.fill((255, 0, 0))
            surface.set_alpha(128)
        else:
            
            if (self.isTurn):
                self.color = (255, 215, 0)
            elif (self.win):
                self.color = (0, 255, 0)
            elif (self.isDealer):
                self.color = (0, 0, 255)
            else:
                self.color = (0, 0, 0)
            surface.fill(self.color)
            surface.set_alpha(255)

        win.blit(surface, pos)
        #pygame.draw.rect(win, self.color, self.rect)
        
    #resets all necessary player attributes to begin a new round.
    def reset(self):
        self.isBig = False
        self.isSmall = False
        self.isDealer = False
        self.isTurn = False
        self.bet = -1
        self.hand = [None, None]
        self.win = False
        self.evaluation = ""
        self.total_bet = 0
        self.in_game = True
        if (self.money != 0):
            self.folded = False
        else:
            self.folded = True
    
    #updates the player x and y information when needed.
    def update(self):
        self.rect = (self.x, self.y, self.WIDTH, self.HEIGHT)
    
    #gets the player name
    def getName(self):
        return self.name
    
    #get the player's x
    def x(self):
        return self.x
    
    #get the player's y
    def y(self):
        return self.y
    
    