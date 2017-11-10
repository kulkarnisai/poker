#
# Author: Sai Kulkarni
# Email: saikulkarni0@gmail.com
# Project Title: Identifying the 'hand' in Texas Hold'em Poker
#
# Under Texas Hold'em poker rules, each player holds 2 cards in their hand. 
# 5 additional cards are revealed on the table and shared by all players. 
# From 5 table cards and 2 cards in his hands, each player can 
# claim an optimal hand of 5 cards.
# https://en.wikipedia.org/wiki/Texas_hold_'em
#
# Each playing card can be represented with the following attributes: 
#    1. A string indicating the suit
#    2. A number from 1-13, indicating value, where face cards are asigned numeric 
#       values as follows: Jack = 11, Queen = 12, King = 13.
#    3. Ace can take 2 values, Ace = 1 for (Ace, 2, 3, 4, 5, ...) and 
#       Ace = 14 for (10 Jack Queen King Ace)
#
# The ranking of hands in Texas Hold'em rules is as follows:
#
# 1. Straight flush      5 Consecutive values of same suit 
# 2. Four of a Kind      4 cards of the same value 
# 3. Full House          3 Cards of the same value and 1 pair of different value
# 4. Flush               5 cards of the same suit
# 5. Straight            5 cards of any suit with consecutive values
# 6. Three of a kind     3 cards of same value
# 7. Two pair            2 pairs of 2 cards with same value
# 8. One pair            2 cards with same value
# 9. High card           Using highest value card for comparison, in absence other hands
#
# 
# This code sample contains the following components: 
#    1. getRank: Given  a list of 5 table cards and a list of 2 player cards, 
#       this returns the rank of the best hand possible for that player
#    2. dealCards : Given a number of players, this function returns the list of table cards 
#    and list of lists of player cards
#    3. Unit tests to make sure 'getRank' returns correct rank for each possible hand from above list
#    4. Simulation to deal cards for 3 players, get their ranks and order them according to rank
# Note: For now, the case where 2 players have same rank and the tie-break depends on 
# the values of cards in their hand is not handled. For example, a hand with pair of 3s and hand with pair of 
# 10s currently will have the same rank
#

import itertools # For generating deck of cards using cartesian product 
import random # For dealing cards
import numpy as np

# Suit names
S = 'Spade'
H = 'Heart'
C = 'Club'
D = 'Diamond'

# Rank values for each hand
STRAIGHT_FLUSH = 0
FOUR_KIND = 1
FULL_HOUSE = 2
FLUSH = 3
STRAIGHT = 4
THREE_KIND = 5
TWO_PAIR = 6
ONE_PAIR = 7
HIGH_CARD = 8

# Names of hands
HAND_NAMES = ["Straight_flush", "Four_kind", "Full_House", "Flush", "Straight", "Three_kind", 
         "Two_pair", "One_pair", "High_card"]

# Possible values for Ace for calculating straight
ACE_LOW = 1
ACE_HIGH = 14

# Checks if a given set of card values contains 5 consecutive values
#   - Ace can form 2 straights: (Ace 2 3 4 5) and (10 Jack Queen King Ace)
def isstraight(values):
    if ACE_LOW in values:
        values.append(ACE_HIGH)
    values.sort()
    prevval = values[0]
    count = 1
    for value in values[1:]:
        if value - prevval == 1:
            count +=1
        else:
            count = 1       
        if count == 5:
            break
        prevval = value 
    if count == 5:
        return True
    else:
        return False
            
# Checks if a given hand contains a straight flush by checking the following conditions:
#        - it contains a flush (at least 5 cards of same suit)
#        - the cards from same suit contain a straight
        
def isstraightflush(countsbysuit, cardsbysuit):
    max_suit = max(countsbysuit, key=countsbysuit.get)
    if countsbysuit[max_suit] < 5:
        return False
    else:
        return isstraight(cardsbysuit[max_suit])


# Checks if a hand is a full house by making sure that the following conditions are met:
#        -if there is one set of 3 cards with same values:
#        -if there is another set of 2/3 cards with same values
# The second condition can also be formutaed as: there are at most 2 values with count = 1      
def isfullhouse(countsbyvalue):
    _isfullhouse = False
    if 3 in countsbyvalue.values():
        count_ones = 0
        for count in countsbyvalue.values():
            if count == 1:
                count_ones += 1
        if count_ones <=2:
            _isfullhouse = True
    return _isfullhouse
    
    

# Returns the rank of the card from list above given 5 table cards and 2 player cards
def getRank(playercards, tablecards): 
    fullhand = tablecards + playercards
    
    # Preprocess to generate 3 data structures: 
    # - dictionary of list of cards by suits
    # - dictionary of number of cards for each value
    # - all cards sorted by value in descending order
    
    cardsbysuit = {} # cards from each suit
    countsbysuit = {} # number of cards from each suit
    countsbyvalue = {} # number of cards of each value 
    for suit, value in fullhand:     
        if suit in cardsbysuit:
            cardsbysuit[suit].append(value)
            countsbysuit[suit] += 1
        else:
            cardsbysuit[suit] = [value]
            countsbysuit[suit] = 1          
        if value in countsbyvalue:
            countsbyvalue[value] += 1
        else:
            countsbyvalue[value] = 1
    
    # Check each hand in ascending order of rank
    if isstraightflush(countsbysuit, cardsbysuit):
        # check if straight flush exists
        rank = STRAIGHT_FLUSH
    elif 4 in countsbyvalue.values():
        # checks if any value occurs 4 times
        rank = FOUR_KIND
    elif isfullhouse(countsbyvalue):
        # checks if there exists a value with 3 cards and another value with 2 cards
        rank = FULL_HOUSE
    elif max(countsbysuit.values()) >= 5:
        # checks if any suit has 5 or higher number of cards in the set of 7
        rank = FLUSH
    elif isstraight(list(countsbyvalue.keys())):
        # checks if any 5 cards have consecutive values
        rank = STRAIGHT
    elif 3 in countsbyvalue.values():
        # checks if any value occurs 3 times
        rank = THREE_KIND
    elif 2 in countsbyvalue.values():
        numpairs = 0
        for count in countsbyvalue.values():
            if count == 2:
                numpairs += 1
        if numpairs >= 2:
            # More than 1 pair detected
            rank = TWO_PAIR
        else: 
            # Exactly 1 pair detected
            rank = ONE_PAIR
    else:
        # No other combination exists
        rank = HIGH_CARD
    
    return rank


# Randomly deals 2 cards to each player and 5 on the table
def dealCards(numPlayers=1):

    suits = [S, H, C, D]
    values = list(range(ACE_LOW, ACE_HIGH))
    deck = itertools.product(suits, values)
    deck = set(deck) # random.sample needs set input
    
    playercards = []
    for _ in range(numPlayers):
        cards = random.sample(deck, 2)
        for card in cards:
            deck.remove(card) 
        playercards.append(cards)
    
    tablecards = random.sample(deck, 5)
    for card in tablecards:
        deck.remove(card)

    return (playercards, tablecards,)

# Test each type of hand:

def runtest(pc, tc, expected):
    name = HAND_NAMES[expected]
    print("TEST: " + name)
    rank = getRank(pc, tc)
    if  rank == expected:
        print("SUCCESS")
    else:
        print("ERROR: TEST FAILED: "+ name)


# Straight Flush
pc = [(S, 3), (S, 7)]
tc = [(D, 2), (S, 4), (S, 5), (C, 13), (S, 6)]
runtest(pc, tc, STRAIGHT_FLUSH)
    
    
# Four of a kind
pc = [(S, 3), (H, 3)]
tc = [(D, 3), (S, 4), (S, 5), (C, 3), (S, 6)]
runtest(pc, tc, FOUR_KIND)

# Full House
pc = [(S, 3), (H, 3)]
tc = [(D, 3), (S, 14), (S, 5), (C, 5), (C, 11)]
runtest(pc, tc, FULL_HOUSE)

# Flush
pc = [(S, 11), (H, 3)]
tc = [(S, 3), (S, 4), (S, 5), (C, 12), (S, 6)]
runtest(pc, tc, FLUSH)

# Straight
pc = [(S, 10), (D, 8)]
tc = [(H, 9), (S, 4), (S, 5), (C, 12), (H, 11)]
runtest(pc, tc, STRAIGHT)

# Three of a kind
pc = [(S, 10), (D, 5)]
tc = [(H, 9), (S, 4), (S, 5), (C, 12), (H, 5)]
runtest(pc, tc, THREE_KIND)

# Two Pair
pc = [(S, 10), (D, 5)]
tc = [(H, 9), (S, 4), (S, 5), (C, 12), (H, 10)]
runtest(pc, tc, TWO_PAIR)

# One pair
pc = [(S, 10), (D, 5)]
tc = [(H, 9), (S, 4), (S, 7), (C, 12), (H, 10)]
runtest(pc, tc, ONE_PAIR)

# High card
pc = [(S, 10), (D, 5)]
tc = [(H, 2), (S, 4), (S, 7), (C, 12), (H, 3)]
runtest(pc, tc, HIGH_CARD)

print("\n\n")


# Simulation:
# With randomly dealt hands, generate a ranking order for all players.
# As mentioned earlier We are currently not handling the case where 'rank' is 
# same for two players and the tie-breaker depends on the value of the cards 
# in their hand

print("SIMULATION: Multiplayer game")
playercards, tablecards = dealCards(3)
print("Table Cards")
print(tablecards)
ranks = []

for pc in playercards:
    rank = getRank(pc, tablecards)
    ranks.append(rank)
sorted_order = np.argsort(np.array(ranks))

for idx in list(sorted_order):
    print("Player " + str(idx) + " has a " + HAND_NAMES[ranks[idx]])
    print("Player " + str(idx) + " cards " + str(playercards[idx]))

    
