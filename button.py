import pygame
from player import Player

#
# Represents a button that can be clicked.
#
class Button():
    pygame.init()
    font = pygame.font.Font(None, 36)
    
    #initializer for the button
    def __init__(self, x, y, text):
        self.height = 50
        self.width = 150
        self.x = x
        self.y = y
        self.text = text
        self.color = (255, 255, 255)
        self.rect = (self.x, self.y, self.width, self.height)
        self.visible = True
    
    #updates the rect of the button.
    def update(self):
        self.rect = (self.x, self.y, self.width, self.height)
        
    #returns true if was clicked, false otherwise.
    def isClicked(self):
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        if (self.x <= mouse_x <= self.x + self.width) and (self.y <= mouse_y <= self.y + self.height) and self.visible and mouse_click[0]:
            return True
        return False
    
    #draws the button to the screen.
    def draw(self, win):
        if (self.visible):
            pygame.draw.rect(win, self.color, self.rect)
            # Render the button text and add it to the screen
            button_text_surface = self.font.render(self.text, True, (0, 0, 0))  # render the text
            button_text_rect = button_text_surface.get_rect()  # get the dimensions of the text
            button_text_rect.center = (self.x + self.width / 2, self.y + self.height / 2)  # center the text on the button
            win.blit(button_text_surface, button_text_rect) 
            

#
# Button that be clicked and text can be typed inside.
#
class InputButton(Button):
    pygame.init()
    font = pygame.font.Font(None, 36)
    
    #initializes the button.
    def __init__(self, x, y, text, type):
        super().__init__(x, y, text)
        self.been_clicked = False
        self.height = 36
        self.type = type
        self.done = False
        
    #draws the button to the screen.
    def draw(self, win):
        if (self.visible):
            text_surface = self.font.render(self.text, True, (0, 0, 0))  # render the text
            text_rect = text_surface.get_rect()
            if (self.text == ""):
                self.width = 50
            else:
                self.width = text_surface.get_width()
                self.height = text_surface.get_height()
            text_rect.center = (self.x + self.width / 2, self.y + self.height / 2)
            super().update()
            pygame.draw.rect(win, self.color, self.rect)
            win.blit(text_surface, text_rect)
    
    
    #determines if button was clicked.
    def isClicked(self):
        if (super().isClicked() and not self.been_clicked):
            self.done = False
            self.been_clicked = True
            self.text = ""
    
    #method to manage all necessary requirements for button functionality.
    def run(self, win):
        self.isClicked()
        self.update()
        self.draw(win)
        #self.key_pressed(event)
        
    
    #updates the button 
    def update(self):
        super().update()
        if (self.done and self.type != "chat"):
            self.visible = False
    
    
    
    def key_pressed(self, event):
        
        #makes sure the player name cannot leave their player cube.
        if (self.width >= Player.WIDTH and self.type != "chat"):
            self.text = self.text[:-1]
        
        #first type clicking button
        if (self.been_clicked and self.visible):
            
            #delete character
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            #submit text
            elif event.key == pygame.K_RETURN:
                self.been_clicked = False
                self.done = True
            #special case for the space key
            elif event.key == pygame.K_SPACE:
                self.text += ' '
            #append character to text.
            else:
                self.text += event.unicode
           
