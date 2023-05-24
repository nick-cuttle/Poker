import pygame
from button import InputButton 

#
# Class that implements the chat functionality.
#
class Chat():
    
    #initializes the chat box.
    def __init__(self, x, y):
        self.chat_button = InputButton(x, y, "Chat: ", "chat")
        self.chat_button.y = self.chat_button.y - self.chat_button.height
        self.chat_button.update()
        self.messages = []
        self.msg_y = [self.chat_button.y - 50, self.chat_button.y - 100, self.chat_button.y - 150, self.chat_button.y - 200, self.chat_button.y - 250]
        
    #draws the chat box to the screen
    def draw(self, win, player, net):
        self.chat_button.run(win)
        if (self.chat_button.done):
            self.append_message(self.chat_button.text, player)
            self.chat_button.done = False
            self.chat_button.text = "Chat: "
            net.send({"type": "sent_message", "data": self.messages})
        self.messages = net.send({"type": "messages", "data": None})["data"]
        self.update_pos()
        for msg in self.messages:
            msg.draw(win)
    
    #updates all the message positions accordingly when new messages are added.
    def update_pos(self):
        for i in range(0, len(self.messages)):
            cur_msg = self.messages[i]
            cur_msg.y = self.msg_y[i]
                
    #adds a message to the chat box.
    def append_message(self, text, player):
        
        #ensures only 5 messages are displayed at a time.
        if (len(self.messages) == 5):
            self.messages.pop(len(self.messages) - 1)
        
        msg = Message(self.chat_button.x, self.chat_button.y, text, player)
        self.messages.insert(0, msg)
        
        #shifts the messages up.
        for i in range(1, len(self.messages)):
            cur_msg = self.messages[i]
            cur_msg.y = self.msg_y[i]

#
# A class to represent a single message.
#
class Message(Chat):
    pygame.init()
    font = pygame.font.Font(None, 36)
    
    #creates a message object.
    def __init__(self, x, y, text, player):
        self.x = x
        self.y = y
        self.player = player
        self.text = player.name + ": " + text
        render = self.font.render(self.text, True, (255, 255, 255))
        self.width = render.get_width()
        self.y = self.y - self.width
    
    #string representation of a message.
    def __repr__(self):
        return f'msg:{self.text}'
    
    #draws a message to the screen.
    def draw(self, win):
        txt = self.font.render(self.text, True, (255, 255, 255))
        win.blit(txt, (self.x, self.y))