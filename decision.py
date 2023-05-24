import pygame
from button import Button

#
# Class to handle all decision making for the client.
#
class Decision():
    pygame.mixer.init()
    font = pygame.font.Font(None, 36)
    #WIDTH = self.bet_button.width + self.check_fold_button.width + self.scale_width + 50
    
    #initializes all decision requirements.
    def __init__(self, x, y):
        
        #the bet button
        self.bet_button = Button(x, y, "Bet")
        self.bet_button.width = 100
        self.bet_button.update()
        self.bet_amount = 0
        self.bet_text = self.font.render(str(self.bet_amount), True, (255, 255, 255))
        
        #the bet/fold button.
        self.check_fold_button = Button(self.bet_button.x + self.bet_button.width + 25, self.bet_button.y, "Check")
        self.check_fold_button.width = 100
        self.check_fold_button.update()
        
        #the scale to hold the slider.
        self.scale_x = self.check_fold_button.x + self.check_fold_button.width + 25
        self.scale_width = 300
        self.scale_height = 20
        self.scale_y = self.bet_button.y + (self.bet_button.height / 2) - (self.scale_height / 2)
        self.scale = (self.scale_x, self.scale_y, self.scale_width, self.scale_height)
        
        #create the slider.
        self.slider_width = 20
        self.slider_height = 40
        self.slider_x = self.scale_x - (self.slider_width / 2)
        self.slider_y = self.scale_y - (self.scale_height / 2)
        self.slider = Button(self.slider_x, self.slider_y, "|")
        self.slider.width = self.slider_width
        self.slider.height = self.slider_height
        self.slider.update()
        self.slider.movable = False
        
        self.width = self.bet_button.width + self.check_fold_button.width + self.scale_width + 50
        self.height = self.bet_button.height
    
    #get current bet.
    def getCurrentBet(self, network):
        msg = {"type": "current_bet", "data": None}
        return network.send(msg)["data"]
    
    #updates all decision information.
    def update(self, x, y):
        self.bet_button.x = x
        self.bet_button.y = y
        self.check_fold_button.x = self.bet_button.x + self.bet_button.width + 25
        self.check_fold_button.y = y
        self.scale_x = self.check_fold_button.x + self.check_fold_button.width + 25
        self.scale_y = self.bet_button.y + (self.bet_button.height / 2) - (self.scale_height / 2)
        self.scale = (self.scale_x, self.scale_y, self.scale_width, self.scale_height)
        self.slider_x = self.scale_x - (self.slider_width / 2)
        self.slider_y = self.scale_y - (self.scale_height / 2)
        self.slider.x = self.slider_x
        self.slider.y = self.slider_y
        self.bet_button.update()
        self.check_fold_button.update()
        self.slider.update()
        
    
    #hides the decision buttons and slider.
    def hide(self):
        self.check_fold_button.visible = False
        self.bet_button.visible = False
        self.slider.visible = False
        
    #makes visible the decision buttons and slider.
    def show(self):
        self.check_fold_button.visible = True
        self.bet_button.visible = True
        self.slider.visible = True
        
    #handles when the bet button is clicked.
    def handle_bet(self, player, net):
        if (self.bet_button.isClicked()):
            sound = pygame.mixer.Sound('sounds/poker_chip.mp3')
            sound.play()
            player.bet = self.bet_amount
            player.money = player.money - self.bet_amount
            self.hide()
            net.send({"type": "done_turn", "data": player})
    
    #handles when the player checks.     
    def handle_check(self, player, net):
        if (self.check_fold_button.text == "Check" and self.check_fold_button.isClicked()):
            self.hide()
            net.send({"type": "done_turn", "data": player})
    
    #handles when the player folds.  
    def handle_fold(self, player, net):
        if (self.check_fold_button.text == "Fold" and self.check_fold_button.isClicked()):
            self.hide()
            player.folded = True
            net.send({"type": "done_turn", "data": player})
        
    #draws the decision buttons and slider to the screen.
    def draw(self, win, net, player):
        min_dist = 10
        max_dist = min_dist
        min_bet = self.getCurrentBet(net)
        if (min_bet > 0):
            self.check_fold_button.text = "Fold"
        else:
            self.check_fold_button.text = "Check"
         
        if player.bet > 0:
            min_bet = min_bet - player.bet    
        self.bet_button.draw(win)
        self.check_fold_button.draw(win)
        pygame.draw.rect(win, (255, 215, 0), self.scale)
        self.slider.draw(win)
        
        if (abs(self.slider.x + (self.slider.width / 2) - self.scale_x) <= min_dist):
            if (min_bet > player.money):
                self.bet_amount = player.money
            else:
                self.bet_amount = min_bet
        elif (abs(self.slider.x + (self.slider.width / 2) - (self.scale_x + self.scale_width)) <= max_dist):
            self.bet_amount = player.money
        else:
            begin_x = self.scale_x + min_dist
            area = self.scale_width - min_dist - max_dist
            dist = abs(self.slider.x + (self.slider.width / 2) - begin_x)
            ratio = dist / area
            self.bet_amount = min_bet + int(player.money * ratio)
            if self.bet_amount > player.money:
                self.bet_amount = player.money
            
        self.bet_text = self.font.render(str(self.bet_amount), True, (255, 255, 255))
        bet_loc = (self.scale_x + self.scale_width + 10, self.scale_y)
        win.blit(self.bet_text, bet_loc)
    
    #implements sliding functionality for the scale.
    def slide(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_pressed= pygame.mouse.get_pressed()
        if (self.scale_x <= mouse_x <= self.scale_x + self.scale_width) and mouse_pressed[0]:
            self.slider.x = mouse_x
            self.slider.update()
        
            