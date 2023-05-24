import socket
from _thread import *
from player import Player
from card import Card
from deck import Deck
import pickle
import pygame
from hand_evaluator import hand_evaluator

#INFORMATION REGARDING SERVER IP AND PORT
server = "192.168.1.229"
port = 8000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#BIND SEVER AND PORT TO A SOCKET.
try:
    s.bind((server, port))
except socket.error as e:
    str(e)

#LISTEN TO A MAXIMUM OF 6 CONNECTIONS
s.listen(6)
print("Waiting for a connection, Server Started")

#MESSAGE FORMAT TO SEND BACK TO CLIENT
def messageFormat(ty, data):
    dic = {"type": ty, 
            "data": data}
    return dic

#ARRAYS CONTAINING ALL PLAYERS AND CLIENTS
players = []
clients = []

poker_running = False #stores if poker has been started
deck = Deck() #initializes the deck
small_blind = 1 # price of small blind
big_blind = 2 * small_blind # price of big blind
cur_bet = big_blind #holds the current bet
dealer_index = 0 #index of the dealer in player array
total_money = 0 # total money in the pot
curPlayer = None #the current player who is in turn
shared_cards = [] #holds all the shared cards in the middle
done_betting = False #holds the state of if betting has terminated.
round_restart = False #holds state of if game needs to be restarted.
GREEN = (0, 255, 0)

messages = [] # holds all messages sent from clients

#send message to all clients
def sendToAll(msg):
    for c in clients:
        c.sendall(pickle.dumps(msg))

#removes a player by name   
def remove_by_name(name):
    global players
    copy = []
    index = 0
    for p in players:
        if (p.name != name):
            p.index = index
            index += 1
            copy.append(p)
    players = copy

#determines who is first to act.
def first_to_act():
    index = dealer_index
    dealer = players[index]
    index = (index + 1) % len(players)
    next = players[index]
    while (next.folded):
        index = (index + 1) % len(players)
        next = players[index]
    return next

#returns all players remaining
def players_remaining():
    remaining = []
    for p in players:
        if not p.folded:
            remaining.append(p)
    return remaining

#sets all the player's bets to b, usually -1 to restart.
def setBets(b):
    global players
    for i in range(0, len(players)):
        p = players[i]
        p.bet = b

#controls the flow of the game for poker.        
def poker():
    global players
    global poker_running
    global dealer_index
    global curPlayer
    global shared_cards
    global deck
    global cur_bet
    global round_restart
    
    
    curPlayer = players[(dealer_index + 1) % len(players)] #small_blind
    dealer = assignDealer(dealer_index) #dealer
    deck.dealCards(players, dealer_index) # deals all cards to the players
    curPlayer.isTurn = True #sets the small blind to start their turn
    
    while poker_running:
        
        rem_players = players_remaining()
        #only one player remaining at start of round, a game winner.
        if (len(rem_players) == 1):
            print(rem_players[0].name + " Has Won!!!!!")
            break
        
        round_restart = False
        while not round_restart:
            
            betting() #PreFlop
            if (len(players_remaining()) == 1):
                round_restart = True
                continue
            
            flop = deck.dealFlop() #flop
            shared_cards.append(flop[0])
            pygame.time.delay(500)
            shared_cards.append(flop[1])
            pygame.time.delay(500)
            shared_cards.append(flop[2])
            setBets(-2)
            cur_bet = 0
            curPlayer = first_to_act()
            curPlayer.isTurn = True
            current_evaluations()
            
            betting() #PostFlop
            if (len(players_remaining()) == 1):
                round_restart = True
                continue
            shared_cards.append(deck.dealTurn())
            setBets(-2)
            cur_bet = 0
            curPlayer = first_to_act()
            curPlayer.isTurn = True  
            current_evaluations()
            
            betting() #PostTurn
            if (len(players_remaining()) == 1):
                round_restart = True
                continue
            shared_cards.append(deck.dealRiver())
            setBets(-2)
            cur_bet = 0
            curPlayer = first_to_act()
            curPlayer.isTurn = True
            current_evaluations()
            
            betting() #PostRiver
            if (len(players_remaining()) == 1):
                round_restart = True
                continue
            
            curPlayer.isTurn = False
            round_restart = True
        
        reset_round()
            
            #pygame.time.delay(10000)

#get the current hand evaluations of all players                 
def current_evaluations():
    global players
    for p in players:
        eval = hand_evaluator(p, p.hand + shared_cards)
        eval.current_evaluation()
        cur_ev = eval.evaluation["type"].replace("_", " ")
        p.evaluation = cur_ev

#resets the round
def reset_round():
    global players
    global deck
    global dealer_index
    global cur_bet
    global big_blind
    global shared_cards
    global total_money
    global curPlayer
    global round_restart
    
    curPlayer.isTurn = False
    
    #determines winners.
    winners = players_remaining()
    if (len(players_remaining()) != 1):
        winners = hand_evaluator.determine_winners(players, shared_cards)
    
    #splits the money between all winners.
    split_money = total_money / len(winners)
    for w in winners:
        w.win = True
        if w.total_win == 0:
            w.money = w.money + split_money
        else:
            w.money = w.money + w.total_win
    
    #resets all the players    
    pygame.time.delay(3000)
    for p in players:
        p.reset()
        
    #resets the deck
    deck = Deck()
    deck.shuffle()
    
    #updates dealer.
    dealer_index = (dealer_index + 1) % len(players)
    while (players[dealer_index].folded):
        dealer_index = (dealer_index + 1) % len(players)
        
    #resets necessary variables.
    cur_bet = big_blind
    shared_cards = []
    total_money = 0
    
    #sets dealer, small, and big blind
    round_restart = False
    curPlayer = players[(dealer_index + 1) % len(players)] #small_blind
    assignDealer(dealer_index)
    deck.dealCards(players, dealer_index)
    curPlayer.isTurn = True
    
    
#updates all player indexes if someone leaves. 
def update_player_index():
    global players
    for i in range(0, len(players)):
        player = players[i]
        player.index = i

#handles betting flow.
def betting():
    global curPlayer
    global cur_bet
    global done_betting
    done_betting = False
    while (not done_betting):
        if (len(players_remaining()) == 1):
            done_betting = True
        continue

#determines if a player is done betting
def is_done_betting():
    global curPlayer
    global done_betting
    if (curPlayer.bet == cur_bet):
        done_betting = True
    elif (cur_bet == 0 and curPlayer.isSmall):
        done_betting = True
        
    else:
        curPlayer.isTurn = True
        
#assigns the dealer, small, and big blind given a dealer index.     
def assignDealer(index):
    
    dealer = players[index]
    dealer.isDealer = True
    dealer.isSmall = False
    dealer.isBig = False
    
    smallPlayer = players[(index + 1) % len(players)]
    smallPlayer.isDealer = False
    smallPlayer.isSmall = True
    smallPlayer.isBig = False
    #smallPlayer.isTurn = True
    
    bigPlayer = players[(index + 2) % len(players)]
    if (len(players) != 2):
        bigPlayer.isDealer = False
        bigPlayer.isSmall = False
        bigPlayer.isBig = True
    else:
        return bigPlayer
    
    return dealer

#threaded function to handle each client
def threaded_client(conn, player):
    #global players
    # conn.send(pickle.dumps(players[player]))
    reply = ""
    while True:
        global players
        global poker_running
        global deck
        global dealer_index
        global cur_bet
        global small_blind
        global big_blind
        global curPlayer
        global total_money
        global done_betting
        global shared_cards
        global round_restart
        global messages
        try:
            
            #load any received client messages
            data = pickle.loads(conn.recv(2048))

            if not data:
                print("Disconnected")
                break
            else:
                #new player added
                if (data["type"] == "new_player"):
                    players.append(data["data"])
                    reply = messageFormat("players", players)
                #update player information
                elif (data["type"] == "update"):
                    if (poker_running):
                        index = data["index"]
                        #dealer_index = index
                        oldPlayer = players[index]
                        newPlayer = data["data"]
                        
                        if (oldPlayer.win == False):
                            oldPlayer.money = newPlayer.money
                        oldPlayer.color = newPlayer.color
                        newPlayer.evaluation = oldPlayer.evaluation
                        #oldPlayer.folded = newPlayer.folded
                        reply = messageFormat("players", players)
                    else:
                        index = data["index"]
                        players[index] = data["data"]
                        reply = messageFormat("players", players)
                #start poker sent
                elif (data["type"] == "start_poker"):
                    poker_running = True
                    deck.shuffle()
                    dealer_index = data["data"]       
                    reply = messageFormat(None, None)
                    start_new_thread(poker, ())
                
                #return current bet to client
                elif (data["type"] == "current_bet"):
                    reply = messageFormat(None, cur_bet)
                
                #return small and big blinds to client
                elif (data["type"] == "blinds"):
                    reply = messageFormat(None, (small_blind, big_blind))
                
                #client indicated done with turn
                elif (data["type"] == "done_turn"):
                    player = data["data"]
                    curPlayer.money = player.money
                    curPlayer.bet = player.bet
                    curPlayer.folded = player.folded
                    if (curPlayer.bet > 0):
                        total_money += curPlayer.bet
                    if (curPlayer.money == 0 and curPlayer.in_game and not curPlayer.folded):
                        curPlayer.total_win = total_money
                        curPlayer.in_game = False
                    if (curPlayer.bet > cur_bet):
                        cur_bet = curPlayer.bet
                    curPlayer.isTurn = False
                    curPlayer = players[(curPlayer.index + 1) % len(players)]
                    #curPlayer.isTurn = True
                    is_done_betting()
                    reply = messageFormat(None, None)
                
                #return shared cards to client.
                elif (data["type"] == "shared_cards"):
                    reply = messageFormat(None, shared_cards)
                
                #send total pot money to client.
                elif (data["type"] == "total_money"):
                    reply = messageFormat(None, total_money)
                #send round restart to client.
                elif (data["type"] == "round_restart"):
                    reply = messageFormat(None, round_restart)
                #client sent a message.
                elif (data["type"] == "sent_message"):
                    messages = data["data"]
                    reply = messageFormat(None, None)
                #send all messages back to client.
                elif (data["type"] == "messages"):
                    reply = messageFormat(None, messages)
                #remove a player from the game.
                elif (data["type"] == "remove_player"):
                    remove_by_name(data["data"].name)
                    #update_player_index()
                    reply = messageFormat(None, None)

                #print("Received: ", data)
                #print("Sending : ", reply)
                
            #sendToAll(reply)
                conn.sendall(pickle.dumps(reply))
        except:
            break

    print(curPlayer.name + " Lost connection")
    conn.close()
    

currentPlayer = 0
#accepts new players and starts a thread for them.
while True:
    
    conn, addr = s.accept()
    #newPlayer = Player(50, 50)
    #players.append(newPlayer)
    clients.append(conn)
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1
    

    