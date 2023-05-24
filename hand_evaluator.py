
from card import Card
from itertools import combinations

#
# Class that deals with evaluating a hand and ranking all players hands
# to determine winner and or split pots.
#
# Is represented in format {"type": "type", "result": integer} where type refers
# to the common ranking of a hand (high_card, two_pair, etc...), while result refers to
# information regarding the type, such as an integer for one pair, an array [int1, int2] for two
# pair, the highest card value in a straight, and so on.
#
class hand_evaluator():
    
    #initializes hand evaluation for round.
    def __init__(self, player, cards):
        self.player = player
        self.cards = cards
        cards.sort()
        self.evaluation = None
        self.tied = None
        
    
    #return string representation of evaluation.
    def __str__(self):
        return f'{self.player}: {self.evaluation["type"]}:{self.evaluation["result"]}'
    
    #return string representation of evaluation.
    def __repr__(self):
        return f'{self.player}: {self.evaluation["type"]}:{self.evaluation["result"]}'
        
    
    #gives an integer value to a hand type for ranking.
    def type_to_int(self):
        t = self.evaluation["type"]
        if (t == "high_card"):
            return 1
        if (t == "one_pair"):
            return 2
        if (t == "two_pair"):
            return 3
        if (t == "three_kind"):
            return 4
        if (t == "straight"):
            return 5
        if (t == "flush"):
            return 6
        if (t == "full_house"):
            return 7
        if (t == "four_kind"):
            return 8
        return 9
    
    
    #gets the current hand evaluation during the round.
    def current_evaluation(self):
        length = len(self.cards)
        for i in range(0, 7 - length):
            self.cards.append(Card(-1 - i, "None"))
        self.evaluateHand()
    
    #removes all cards in a hand with the same value.     
    def removeByVal(self, val):
        cards_updated = [value for value in self.cards if value.val != val]
        self.cards = cards_updated
        self.cards.sort()
                
    #reevaluates a hand if players have same type and need to go to high card and such.
    def re_evaluate(self):
        types = ["high_card", "one_pair", "three_kind", "four_kind"]
        t = self.evaluation["type"]
        if (t in types):
            #removes the identical cards.
            self.removeByVal(self.evaluation["result"])
            
            #determine if tie or not.
            if (len(self.cards) <= 2):
                self.evaluation["result"] = 0
            else:
                self.evaluation["result"] = self.high_card(self.cards)
            return len(self.cards)
                
    #compares two full houses.  
    def compare_full_house(self, other):
        if (self.evaluation["result"][0] == other.evaluation["result"][0]):
            if (self.evaluation["result"][1] == other.evaluation["result"][1]):
                return self.evaluation["result"] < other.evaluation["result"]
            else:
                return self.evaluation["result"][1] < self.evaluation["result"][1]
        else:
            return self.evaluation["result"][0] < self.evaluation["result"][0]
        
    #compares two two pairs
    def compare_two_pair(self, other):
        if (self.evaluation["result"][1] == other.evaluation["result"][1]):
                if (self.evaluation["result"][0] != other.evaluation["result"][0]):
                    return self.evaluation["result"][0] < self.evaluation["result"][0]
        else:
            return self.evaluation["result"][1] < self.evaluation["result"][1]
        
    #compares two flushes.
    def compare_flushes(self, other):
        sum1 = 0
        sum2 = 0
        for s in self.evaluation["result"]:
            sum1 += s
        for s in other.evaluation["result"]:
            sum2 += s
        return sum1 < sum2
        
    
    #sorting algorithm to rank hands
    def __lt__(self, other):
        int1 = self.type_to_int()
        int2 = other.type_to_int()
        og1_cards = self.cards.copy()
        og2_cards = other.cards.copy()
        og1_ev = self.evaluation["result"]
        og2_ev = other.evaluation["result"]
        
        #if two players the same hand type.
        if (int1 == int2):
            
            #if two players have the same result and need further evaluation
            if (self.evaluation["result"] == other.evaluation["result"]):
                
                #if any of these types, automatic tie.
                if (self.evaluation["type"] in ["straight", "straight_flush", "flush", "full_house"]):
                    self.tied = True
                    other.tied = True
                    return self.evaluation["result"] < self.evaluation["result"]
                
                #special case for two pair.
                if (self.evaluation["type"] == "two_pair"):
                    self.removeByVal(self.evaluation["result"][0])
                    other.removeByVal(self.evaluation["result"][1])
                    h1 = self.high_card(self.cards)
                    h2 = other.high_card(other.cards)
                    #if share same high card, tie.
                    if (h1 == h2):
                        self.tied = True
                        other.tied = True
                    return h1 < h2
                
                #evaluate again.
                self.re_evaluate()
                other.re_evaluate()
                #keep re-evaluating while the two players have the same hand until no longer possible.
                while (self.evaluation["result"] != 0 and self.evaluation["result"] == other.evaluation["result"]):
                    self.re_evaluate()
                    other.re_evaluate()
                self.cards = og1_cards
                self.cards = og2_cards
                compare = (self.evaluation["result"], other.evaluation["result"])
                #determine if tie.
                if (compare[0] == 0 and compare[1] == 0):
                    self.tied = True
                    other.tied = True
                    
                #set the player evaluations
                self.evaluation["result"] = og1_ev
                other.evaluation["result"] = og2_ev
                return compare[0] < compare[1]
             
            else:
                #same type, different result, so compare them.
                
                if (self.evaluation["type"] == "full_house"):
                    return self.compare_full_house(other)
                elif (self.evaluation["type"] == "two_pair"):
                    return self.compare_two_pair(other)
                elif (self.evaluation["type"] == "flush"):
                    return self.compare_flushes(other)
                
                
                return self.evaluation["result"] < other.evaluation["result"]
              
        else:
            #not the same types, rank them by their integer conversion value.
            return int1 < int2
            
    @classmethod
    #ranks all the players hands and determines all winners.
    def determine_winners(cls, players, shared_cards):
        
        #arrays to hold the winners and all players evaluations.
        winners = []
        evals = []
        
        #for each player gets their evaluation and adds to evals array.
        for p in players:
            if (not p.folded):
                #creates each players 7 card hand.
                cards = shared_cards.copy()
                cards.append(p.hand[0])
                cards.append(p.hand[1])
                
                #evaluates the hand
                eva = hand_evaluator(p, cards)
                eva.evaluateHand()
                
                #cleans up the evaluation for client display.
                cur_ev = eva.evaluation["type"].replace("_", " ")
                p.evaluation = cur_ev
                evals.append(eva)
        
        #sorts/ranks the evaluations by the criteria found in the __lt__() method.
        evals.sort()
        
        #gets the winning evaluation at the end and automatically appends to winners.
        winner_eval = evals[len(evals) - 1]
        winners.append(winner_eval.player)
        
        #determines if any of the other players tied with the winner, also making them winners.
        for ev in reversed(evals):
            #determines if winner is tied with someone and is not the winner themselves.
            if (ev != winner_eval and winner_eval.tied != None):
                cur_eval = ev.evaluation
                win_eval = winner_eval.evaluation
                
                #determines if current evaluation is tied with the winner, and if so, appends them to winners.
                if (ev.tied != None and cur_eval["type"] == win_eval["type"] and cur_eval["result"] == win_eval["result"]):
                    winners.append(ev.player)
                else:
                    #if next best player is not tied, then the others cannot be, so break early.
                    break
        
        return winners
        
                
    #evaluates the current hand.        
    def evaluateHand(self):
        #sort the cards first.
        
        #determine if straight flush
        self.cards.sort()
        straight_flush = self.is_straight_flush(self.cards)
        if (straight_flush != None):
            self.evaluation = {"type": "straight_flush", "result": straight_flush}
            return
        
        #determine if four of a kind.
        four_kind = self.is_four_of_kind(self.cards)
        if (four_kind != None):
            self.evaluation = {"type": "four_kind", "result": four_kind}
            return
        
        #determine if full house.
        full_house = self.is_full_house(self.cards)
        if (full_house!= None):
            self.evaluation = {"type": "full_house", "result": full_house}
            return
        flush = self.is_flush(self.cards)
        if (flush != None):
            self.evaluation = {"type": "flush", "result": flush}
            return
        
        #determine if straight
        straight = self.is_straight(self.cards)
        if (straight != None):
            self.evaluation = {"type": "straight", "result": straight}
            return
        
        #determine if three of a kind
        three_kind = self.is_three_of_kind(self.cards)
        if (three_kind != None):
            self.evaluation = {"type": "three_kind", "result": three_kind}
            return
        
        #determine if two pair.
        two_pair = self.is_two_pair(self.cards)
        if (two_pair[0] != None and two_pair[1] != None):
            two_pair.sort()
            self.evaluation = {"type": "two_pair", "result": two_pair}
            return
        
        #determine if one pair.
        one_pair = self.is_one_pair(self.cards)
        if (one_pair != None):
            self.evaluation = {"type": "one_pair", "result": one_pair}
            return
        
        #else high card.
        high_card = self.high_card(self.cards)
        self.evaluation = {"type": "high_card", "result": high_card}
    
    
    #determines if a hand is a straight flush 
    def is_straight_flush(self, cards):
        
        #get all five card combinations.
        c = combinations(cards, 5)
        combs = [list(l) for l in c]
        
        clone = cards.copy()
        #convert A's -> 1's
        for i in range(0, len(clone)):
            if (clone[i].val == 14):
                clone[i] = Card(1, clone[i].suit)
        
        #get all five card combinations for the clone with 1's in place of A's.
        c2 = combinations(clone, 5)
        combs2 = [list(l) for l in c2]
        straight_high = None
        
        for comb in combs:
            comb.sort()
            base = comb[0].val
            suits = []
            suits.append(comb[0].suit)
            is_straight = True
            #determine if straight
            for num in range(1, len(comb)):
                suits.append(comb[num].suit)
                if comb[num].val != base + num:
                    is_straight = False
            #determine if straight flush
            if (is_straight and [comb[0].suit]*len(suits) == suits):
                #set the straight high for the evaluation result
                if (straight_high == None):
                    straight_high = comb[4].val
                elif (comb[4].val > straight_high):
                    straight_high = comb[4].val
        
        #repeat above for the cloned combinations.     
        for comb in combs2:
            comb.sort()
            base = comb[0].val
            suits = []
            suits.append(comb[0].suit)
            is_straight = True
            for num in range(1, len(comb)):
                suits.append(comb[num].suit)
                if comb[num].val != base + num:
                    is_straight = False
            if (is_straight and [comb[0].suit]*len(suits) == suits):
                if (straight_high == None):
                    straight_high = comb[4].val
                elif (comb[4].val > straight_high):
                    straight_high = comb[4].val
        
        return straight_high
                
    
    #determines if a hand is a four of a kind.
    def is_four_of_kind(self, cards):
        
        for i in range(0, 4):
            vals = []
            for j in range(0, 4):
                vals.append(cards[i + j].val)
            if ([vals[0]]*len(vals) == vals):
                return cards[i + 3].val
        
        return None
    
    #determines if a hand is a full house
    def is_full_house(self, cards):
        
        #determines whether a three of a kind is present.
        three = self.is_three_of_kind(cards)
        if (three == None):
            return None
        
        #determine if there is a two pair.
        two = None
        for i in range(0, len(cards) - 1):
            vals = []
            for j in range(0, 2):
                vals.append(cards[i + j].val)
            if ([vals[0]]*len(vals) == vals and vals[0] != three):
                two = vals[0]
        
        #return None if no two pair exists.
        if (two == None):
            return None
        return [three, two]
    
    
    #determine if a hand is a flush.  
    def is_flush(self, cards):
        h = []
        s = []
        d = []
        c = []
        
        #count the number of suits.
        for i in range(0, len(cards)):
            val = cards[i].val
            suit = cards[i].suit
            if suit == "H":
                h.append(val)
            if suit == "D":
                d.append(val)
            if suit == "C":
                c.append(val)
            if suit == "S":
                s.append(val)
        
        #find if a flush exists and sort it.
        flush = None
        if (len(h) >= 5):
            flush = h
            flush.sort()
        if (len(s) >= 5):
            flush = s
            flush.sort()
        if (len(d) >= 5):
            flush = d
            flush.sort()
        if (len(c) >= 5):
            flush = c
            flush.sort()
        
        #remove any unnecessary extra suits not relevant to flush value.
        while (flush != None and len(flush) > 5):
            flush.pop(0)
        return flush
        
    #determines if a hand is a straight
    def is_straight(self, cards):
        c = combinations(cards, 5)
        combs = [list(l) for l in c]
        
        clone = cards.copy()
        #convert A's -> 1's
        for i in range(0, len(clone)):
            if (clone[i].val == 14):
                clone[i] = Card(1, clone[i].suit)
        
        c2 = combinations(clone, 5)
        combs2 = [list(l) for l in c2]
        straight_high = None
        
        #go through each combination looking for straight
        for comb in combs:
            comb.sort()
            base = comb[0].val
            is_straight = True
            
            #determine if it is a straight
            for num in range(1, len(comb)):
                if comb[num].val != base + num:
                    is_straight = False
            if (is_straight):
                #set straight high if none or override if bigger than previous
                if (straight_high == None):
                    straight_high = comb[4].val
                elif (comb[4].val > straight_high):
                    straight_high = comb[4].val
        
        #repeat for all combinations with 1 instead of ace      
        for comb in combs2:
            comb.sort()
            base = comb[0].val
            is_straight = True
            for num in range(1, len(comb)):
                if comb[num].val != base + num:
                    is_straight = False
            if (is_straight):
                if (straight_high == None):
                    straight_high = comb[4].val
                elif (comb[4].val > straight_high):
                    straight_high = comb[4].val
        
        return straight_high

    #determine if a hand is a three of a kind.
    def is_three_of_kind(self, cards):
        high_card = None
        
        #looks at every offset of 3 cards for a three of a kind.
        for i in range(0, 5):
            vals = []
            for j in range(0, 3):
                vals.append(cards[i + j].val)
            if ([vals[0]]*len(vals) == vals):
                high_card = vals[0]
        
        return high_card
    
    #determine if a hand is a two pair.
    def is_two_pair(self, cards):
        pairs = [None, None]
        index = 0
        
        #looks at every offset of 2 cards sorted for pairs.
        for i in range(0, 6):
            vals = []
            for j in range(0, 2):
                vals.append(cards[i + j].val)
            if ([vals[0]]*len(vals) == vals):
                pairs[index] = vals[0]
                index = abs(index - 1)
        return pairs
    
    #determine if a hand is a one pair.
    def is_one_pair(self, cards):
        pair = None
        
        #looks at every offset for a pair of cards.
        for i in range(0, len(cards) - 1):
            vals = []
            for j in range(0, 2):
                vals.append(cards[i + j].val)
            if ([vals[0]]*len(vals) == vals):
                pair = vals[0]
        return pair
    
    #returns the value of the highest card.
    def high_card(self, cards):
        return cards[len(cards) - 1].val
    
    
    
    