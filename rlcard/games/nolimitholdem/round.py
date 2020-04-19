# -*- coding: utf-8 -*-
''' Implement Limit Texas Hold'em Round class
'''

from rlcard.games.limitholdem.round import LimitholdemRound
import numpy as np


class NolimitholdemRound():
    ''' Round can call other Classes' functions to keep the game running
    '''

    def __init__(self, num_players, init_raise_amount):
        ''' Initilize the round class

        Args:
            num_players (int): The number of players
            init_raise_amount (int): The min raise amount when every round starts
        '''
        self.game_pointer = None
        self.num_players = num_players
        self.init_raise_amount = init_raise_amount

        # Count the number without raise
        # If every player agree to not raise, the round is overr
        self.not_raise_num = 0

        # Raised amount for each player
        self.raised = [0 for _ in range(self.num_players)]

    def start_new_round(self, game_pointer, raised=None):
        ''' Start a new bidding round

        Args:
            raised (list): Initialize the chips for each player

        Note: For the first round of the game, we need to setup the big/small blind
        '''
        self.game_pointer = game_pointer
        self.not_raise_num = 0
        if raised:
            self.raised = raised
        else:
            self.raised = [0 for _ in range(self.num_players)]

    def proceed_round(self, players, action, pot):
        ''' Call other Classes's functions to keep one round running

        Args:
            players (list): The list of players that play the game
            action (str/int): An legal action taken by the player

        Returns:
            (int): The game_pointer that indicates the next player
        '''
        if action == 'call':
            diff = max(self.raised) - self.raised[self.game_pointer]
            self.raised[self.game_pointer] = max(self.raised)
            players[self.game_pointer].bet(chips=diff)
            self.not_raise_num += 1

        elif action == 'all-in':
            all_in_quantity = players[self.game_pointer].remained_chips
            self.raised[self.game_pointer] = all_in_quantity
            players[self.game_pointer].bet(chips=all_in_quantity)
            self.not_raise_num = 1

        elif action == 'raise-pot':
            self.raised[self.game_pointer] += pot
            players[self.game_pointer].bet(chips=pot)
            self.not_raise_num = 1

        elif action == 'raise-half-pot':
            quantity = int(pot / 2)
            self.raised[self.game_pointer] += quantity
            players[self.game_pointer].bet(chips=quantity)
            self.not_raise_num = 1

        elif action == 'fold':
            players[self.game_pointer].status = 'folded'
            self.player_folded = True

        elif action == 'check':
            self.not_raise_num += 1

        self.game_pointer = (self.game_pointer + 1) % self.num_players

        # Skip the folded players
        while players[self.game_pointer].status == 'folded':
             self.game_pointer = (self.game_pointer + 1) % self.num_players

        return self.game_pointer

    def get_nolimit_legal_actions(self, players):
        ''' Obtain the legal actions for the curent player

        Args:
            players (list): The players in the game

        Returns:
           (list):  A list of legal actions
        '''
        full_actions = ['call', 'fold', 'check', 'raise-half-pot', 'raise-pot', 'all-in']
        # full_actions = ['call', 'fold', 'check', 'raise-bb', 'raise-3bb', 'raise-half-pot', 'raise-pot', 'all-in']
        # full_actions = ['call', 'fold', 'check', 'all-in']

        # If the current chips are less than that of the highest one in the round, we can not check
        if self.raised[self.game_pointer] < max(self.raised):
            full_actions.remove('check')

        # If the current player has put in the chips that are more than others, we can not call
        if self.raised[self.game_pointer] == max(self.raised):
            full_actions.remove('call')

        if players[self.game_pointer].in_chips + np.sum(self.raised) > players[self.game_pointer].remained_chips:
            full_actions.remove('raise-pot')

        if players[self.game_pointer].in_chips + int(np.sum(self.raised) / 2) > players[self.game_pointer].remained_chips:
            full_actions.remove('raise-half-pot')

        # If the current player has no more chips after call, we cannot raise
        diff = max(self.raised) - self.raised[self.game_pointer]
        if players[self.game_pointer].in_chips + diff >= players[self.game_pointer].remained_chips:
            return ['call']

        # # Append available raise amount to the action list
        # min_raise_amount = max(self.raised) - self.raised[self.game_pointer] + self.current_raise_amount
        # if min_raise_amount <= 0:
        #     raise ValueError("Raise amount {} should not be smaller or equal to zero".format(min_raise_amount))

        # if players[self.game_pointer].in_chips + min_raise_amount < players[self.game_pointer].remained_chips:
        #     for available_raise_amount in range(min_raise_amount, players[self.game_pointer].remained_chips - players[self.game_pointer].in_chips + 1):
        #         full_actions.append(available_raise_amount)

        return full_actions

    def is_over(self):
        ''' Check whether the round is over

        Returns:
            (boolean): True if the current round is over
        '''
        if self.not_raise_num >= self.num_players:
            return True
        return False