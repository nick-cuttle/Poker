import pygame
from network import Network
from player import Player
from card import Card
from button import Button, InputButton
import ctypes
from decision import Decision
from chat import Chat

pygame.init()

#GET THE SCREEN SIZE
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
WIDTH = screensize[0]
HEIGHT = screensize[1]

#CREATE DISPLAY
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client")

#HOLDS ALL PLAYERS IN GAME
players = []

#LOAD POKER TABLE AND FONT SETTINGS FOR GAME
poker_table = pygame.image.load('poker_table.png')
poker_table = pygame.transform.scale(poker_table, (WIDTH, HEIGHT))
font_size = 36
font = pygame.font.Font(None, font_size)
win.blit(poker_table, (0, 0))

#INFORMATION REGARDING CURRENT PLAYER SUCH AS INDEX IN PLAYERS ARRAY, ETC...
name_text = None
curPlayer = None
playerIndex = 0
name_input = InputButton(WIDTH / 2, HEIGHT / 2, "NAME:", "name")

#START BUTTON TO START THE GAME, NEEDS 2 PEOPLE
start_button = Button(WIDTH / 2, HEIGHT / 2, "START GAME")

#SETS THE DEFAULT CARD BACK IMAGE
card_back = pygame.image.load('cards/frog.png')
card_back = pygame.transform.scale(card_back, (Card.WIDTH, Card.HEIGHT))

#HOLDS INFORMATION REGARDING GAME STATE
poker_running = False
restart = False

#ARRAY TO HOLD CARDS IN MIDDLE OF TABLE.
shared_cards = []

#TOTAL MONEY IN THE POT
total_money = 0

#DICTATES HOW THE CARDS SHOULD BE SPACED ON THE SCREEN FOR EACH CLIENT SCREEN
card_spacing = Card.WIDTH + 30
card_x = (WIDTH / 2) - (Card.WIDTH / 2) - (2 * card_spacing)
card_y = (HEIGHT / 2) - (Card.HEIGHT / 2)
CARD_LOCATION = [(card_x, card_y), (card_x + card_spacing, card_y), (card_x + 2 * card_spacing, card_y), (card_x + 3 * card_spacing, card_y), (card_x + 4 * card_spacing, card_y)]

#INITIALIZE DECISION BUTTONS WITH POSITIONS
decision = Decision(500, 500)
dec_x = (card_x + 2 * card_spacing) + (Card.WIDTH / 2) - (decision.width / 2)
dec_y = card_y + Card.HEIGHT + 30
decision.update(dec_x, dec_y)

#INITALIZE CHAT
chat = Chat(0, HEIGHT)

#####SOUNDS########################
flip_card_sound = pygame.mixer.Sound('sounds/flipcard.mp3')
#background_music = pygame.mixer.Sound('sounds/poker_music.mp3')
#background_music.set_volume(0.2)
#background_music.play(loops=-1)


#######--------------TESTING GROUND------------------#######

#test = pygame.image.load('cards/10C.png')
#test = pygame.transform.scale(test, (Card.WIDTH, Card.HEIGHT))
#win.blit(test, (0, 0))
###########################################################

PLAYER_LOCATION = []
#p1
PLAYER_LOCATION.append((WIDTH / 4, HEIGHT - Player.HEIGHT))
#p2
PLAYER_LOCATION.append((WIDTH * (3 / 4) - Player.WIDTH, HEIGHT - Player.HEIGHT))
#p3
PLAYER_LOCATION.append((WIDTH - Player.WIDTH, (HEIGHT / 2) - (Player.HEIGHT / 2)))
#p4
PLAYER_LOCATION.append((PLAYER_LOCATION[1][0], Card.HEIGHT))
#p5
PLAYER_LOCATION.append((PLAYER_LOCATION[0][0], Card.HEIGHT))
#p6
PLAYER_LOCATION.append((0, (HEIGHT / 2) - (Player.HEIGHT / 2)))


#CREATES THE MESSAGE FORMAT TO SEND TO SERVER
def messageFormat(ty, data):
    dic = {"type": ty, 
            "data": data}
    return dic

#MESSAGE REGARDING AN UPDATE MESSAGE
def updateFormat(ty, data, index):
    dic = {"type": ty, 
            "data": data,
            "index": index}
    return dic

#redraws the window each tick
def redrawWindow(win, players, net):
    
    #reference all necessary variables.
    global poker_running
    global decision
    global curPlayer
    global shared_cards
    global CARD_LOCATION
    global total_money
    win.fill((177,177,177))
    
    #draws the poker table.
    pygame.draw.ellipse(win, (77, 40, 0), (0, 0, WIDTH, HEIGHT))
    pygame.draw.ellipse(win, (53, 101, 57), (50, 50, WIDTH - 100, HEIGHT - 100))
    pygame.draw.rect(win, (53, 90, 57), (CARD_LOCATION[0][0], CARD_LOCATION[0][1], Card.WIDTH, Card.HEIGHT))
    pygame.draw.rect(win, (53, 90, 57), (CARD_LOCATION[1][0], CARD_LOCATION[1][1], Card.WIDTH, Card.HEIGHT))
    pygame.draw.rect(win, (53, 90, 57), (CARD_LOCATION[2][0], CARD_LOCATION[2][1], Card.WIDTH, Card.HEIGHT))
    pygame.draw.rect(win, (53, 90, 57), (CARD_LOCATION[3][0], CARD_LOCATION[3][1], Card.WIDTH, Card.HEIGHT))
    pygame.draw.rect(win, (53, 90, 57), (CARD_LOCATION[4][0], CARD_LOCATION[4][1], Card.WIDTH, Card.HEIGHT))
    
    #draws each player.
    for player in players:
        name = font.render(player.name, True, (255, 255, 255))
        player.draw(win, PLAYER_LOCATION[player.index])
        win.blit(name, PLAYER_LOCATION[player.index])
        drawCards(win, player, net)
        if (player.name != curPlayer.name):
            money = font.render("$: " + str(player.money), True, (255, 255, 255))
            money_loc = (PLAYER_LOCATION[player.index][0], PLAYER_LOCATION[player.index][1] + Player.HEIGHT - money.get_height())
            win.blit(money, money_loc)

    #draws chat box.
    chat.draw(win, curPlayer, net)
    
    #only draw start button if game isn't running.
    if (poker_running):
        start_button.visible = False
    else:
        name_input.run(win)
    start_button.draw(win)
    if (start_button.isClicked() and len(players) >= 2):
        startMSG = messageFormat("start_poker", curPlayer.index)
        net.send(startMSG)
        start_button.visible = False
    
    
    if (not name_input.visible):
        curPlayer.name = name_input.text
    
    #updates decision information
    decision.slide()
    decision.draw(win, net, curPlayer)
    
    old_size = len(shared_cards)
    shared_cards = net.send(messageFormat("shared_cards", None))["data"]
    if(len(shared_cards) > old_size):
        flip_card_sound.play()
    
    #updates money information.
    total_money = net.send(messageFormat("total_money", None))["data"]
    pot_text = font.render("Pot: " + str(total_money), True, (255, 255, 255))
    pot_text_x = (card_x + 2 * card_spacing) + (Card.WIDTH / 2) - (pot_text.get_width() / 2)
    win.blit(pot_text, (pot_text_x, card_y - 30))
    
    #updates current client money information.
    cur_money = font.render("$: " + str(curPlayer.money), True, (255, 255, 255))
    cur_money_loc = (PLAYER_LOCATION[curPlayer.index][0], PLAYER_LOCATION[curPlayer.index][1] + Player.HEIGHT - cur_money.get_height())
    win.blit(cur_money, cur_money_loc)
    eval_text = font.render(curPlayer.evaluation, True, (255, 255, 255))
    win.blit(eval_text, (cur_money_loc[0] + cur_money.get_width() + 10, cur_money_loc[1]))
    
    #loads the shared cards on the table.
    for i in range(0, len(shared_cards)):
        card = shared_cards[i]
        card_img = pygame.image.load('cards/' + str(card.val) + card.suit + '.png')
        card_img = pygame.transform.scale(card_img, (Card.WIDTH, Card.HEIGHT))
        win.blit(card_img, CARD_LOCATION[i])

    pygame.display.update()

#draws a players card to the screen.
def drawCards(win, player, n):
    
    global poker_running
    restart = n.send(messageFormat("round_restart", None))["data"]
    
    #draws the current clients hand regardless.
    if (player == curPlayer):
        card1 = curPlayer.hand[0]
        card2 = curPlayer.hand[1]
        if (isinstance(card1, Card)):
            poker_running = True
            win.blit(card1.get_card_image(), (PLAYER_LOCATION[curPlayer.index][0], PLAYER_LOCATION[curPlayer.index][1] - Card.HEIGHT))
        if (isinstance(card2, Card)):
            win.blit(card2.get_card_image(), (PLAYER_LOCATION[curPlayer.index][0] + Card.WIDTH, PLAYER_LOCATION[curPlayer.index][1]- Card.HEIGHT))
    
    #shows other players cards at the end if not folded.
    elif (restart and not player.folded):
        card1 = player.hand[0]
        card2 = player.hand[1]
        x = PLAYER_LOCATION[player.index][0]
        y = PLAYER_LOCATION[player.index][1] - Card.HEIGHT
        if (isinstance(card1, Card)):
            poker_running = True
            win.blit(card1.get_card_image(), (x, y))
        if (isinstance(card2, Card)):
            win.blit(card2.get_card_image(), (x + Card.WIDTH, y))
    
    else:
        #draws the card back for the other players.
        if (poker_running):
            if (isinstance(player.hand[0], Card)):
                win.blit(card_back, (PLAYER_LOCATION[player.index][0], PLAYER_LOCATION[player.index][1] - Card.HEIGHT))
            if (isinstance(player.hand[1], Card)):
                win.blit(card_back, (PLAYER_LOCATION[player.index][0] + Card.WIDTH, PLAYER_LOCATION[player.index][1] - Card.HEIGHT))

#pays small blind if necessary.
def paySmall(net):
    global curPlayer
    
    #player hasn't bet and is small.
    if (curPlayer.bet == -1 and curPlayer.isSmall):
        msg = messageFormat("blinds", None)
        small_blind = net.send(msg)["data"][0]
        if (curPlayer.money < small_blind):
            curPlayer.bet = curPlayer.money
            curPlayer.money = 0
        else:
            curPlayer.money = curPlayer.money - small_blind
            curPlayer.bet = small_blind
            
        net.send(messageFormat("done_turn", curPlayer))
   
#pays big blind if necessary        
def payBig(net):
    global curPlayer
    
    if (curPlayer.bet == -1 and curPlayer.isBig):
        msg = messageFormat("blinds", None)
        big_blind = net.send(msg)["data"][1]
        if (curPlayer.money < big_blind):
            curPlayer.bet = curPlayer.money
            curPlayer.money = 0
        else:
            curPlayer.money = curPlayer.money - big_blind
            curPlayer.bet = big_blind
        
        net.send(messageFormat("done_turn", curPlayer))

#updates to the correct player    
def update_player():
    global curPlayer
    for p in players:
        if p.name == curPlayer.name:
            curPlayer = p

#main method
def main():
    name = ""
    global playerIndex
    global curPlayer
    global restart
    run = True
    
    #initiates network communication
    n = Network()
    p = n.getP()
    
    #initiates player information.
    curPlayer = Player(0, 0, name)
    playerMSG = messageFormat("new_player", curPlayer)
    players = n.send(playerMSG)["data"]
    clock = pygame.time.Clock()
    curPlayer = players[len(players) - 1]
    playerIndex = len(players) - 1
    name_input.x = PLAYER_LOCATION[playerIndex][0]
    name_input.y = PLAYER_LOCATION[playerIndex][1] - name_input.height
    curPlayer.x = PLAYER_LOCATION[playerIndex][0]
    curPlayer.y = PLAYER_LOCATION[playerIndex][1]
    curPlayer.update()
    curPlayer.name = str(playerIndex)
    curPlayer.index = playerIndex;
    print(curPlayer.name)

    while run:
        clock.tick(60)
        
        #event loop to catch key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                name_input.key_pressed(event)
                chat.chat_button.key_pressed(event)
            
        #draw only relevant information if it's their turn.
        if (curPlayer.isTurn):
            
            if (curPlayer.folded or curPlayer.money == 0):
                n.send(messageFormat("done_turn", curPlayer))
            decision.show()
            paySmall(n)
            payBig(n)
            decision.handle_bet(curPlayer, n)
            decision.handle_check(curPlayer, n)
            decision.handle_fold(curPlayer, n)
              
        else:
            decision.hide()
        
        #update players   
        update = updateFormat("update", curPlayer, curPlayer.index)
        players = n.send(update)["data"]
        restart = n.send(messageFormat("round_restart", None))["data"]
        for p in players:
            if p.name == curPlayer.name:
                curPlayer = p
        redrawWindow(win, players, n)
    

main()