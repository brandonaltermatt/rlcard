import numpy as np

class LimitHoldemInfosetEncoder:
    RANK_ORDER = '23456789TJQKA'  # Allows for extension of No Limit Holdem

    def __init__(self):
        self.amount_of_ranks = len(self.RANK_ORDER)
        self.state_size = 26 + self.amount_of_ranks * 4
        self.state_shape = [self.state_size]
        self._encoded_vector = None

    def encode(self, player_state, action_record):
        '''
            Encodes the player state and action record into a binary list info set.
            Refer to the following post for more information:
            https://github.com/jake-bickle/rlcard/issues/11#issuecomment-661328769

            Args:
                player_state (dict): The dict returned by player.get_state()
                action_record (2D array): An array of actions, where an action is an array [player_id, action_string]

            Returns:
                A binary list of the encoded info set
        '''
        self._encoded_vector = np.zeros(self.state_size)
        self._encode_cards(player_state)
        self._encode_bets(player_state['player_id'], action_record)
        return self._encoded_vector

    def _encode_cards(self, player_state):
        if not player_state['hand']:
            return
        self._encode_card_ranks(player_state)
        self._encode_card_suits(player_state)

    def _encode_card_ranks(self, player_state):
        def encode_round_ranks(cards, starting_index):
            for card in cards:
                rank = card[1]
                index = starting_index + self.RANK_ORDER.index(rank)
                if index is not None:
                    self._encoded_vector[index] = 1

        hole_cards = player_state['hand']
        flop_cards = sorted(player_state['public_cards'][:3])
        turn_cards = player_state['public_cards'][3:4]
        river_cards = player_state['public_cards'][4:5]
        encode_round_ranks(hole_cards, 25)
        encode_round_ranks(flop_cards, (25 + self.amount_of_ranks))
        encode_round_ranks(turn_cards, (25 + (self.amount_of_ranks * 2) + 1))
        encode_round_ranks(river_cards, (25 + (self.amount_of_ranks * 3) + 1))
        # If there is a pair in the flop, set 1 if the pair is the higher of the two ranks
        if flop_cards and flop_cards[1][1] != flop_cards[0][1] and flop_cards[1][1] == flop_cards[2][1]:
            self._encoded_vector[25 + self.amount_of_ranks * 2] = 1

    def _encode_card_suits(self, player_state):
        hole_card_suits = [card[0] for card in player_state['hand']]
        community_card_suits = [card[0] for card in player_state['public_cards']]
        suits = 'CDHS'
        pair_suits = []
        for suit in suits:
            suit_occurances = community_card_suits.count(suit)
            if suit_occurances == 4:
                self._encoded_vector[7] = 1
                self._encoded_vector[8] = 1 if suit in hole_card_suits else 0
            if suit_occurances == 3:
                self._encoded_vector[5] = 1
                self._encoded_vector[6] = 1 if suit in hole_card_suits else 0
            if suit_occurances == 2:
                pair_suits.append(suit)
            community_card_suits = [s for s in community_card_suits if s != suit]
        self._encoded_vector[0] = 1 if hole_card_suits[0] == hole_card_suits[1] else 0
        
        if len(pair_suits) == 1:
            self._encoded_vector[1] = 1
            self._encoded_vector[2] = 1 if pair_suits[0] in hole_card_suits else 0
        elif len(pair_suits) == 2:
            self._encoded_vector[1] = 1
            self._encoded_vector[3] = 1
            # The logic here ensures bit 4 is activated only if bit 2 is
            matching_suits = map(lambda s: s in hole_card_suits, pair_suits)
            self._encoded_vector[2] = 1 if any(matching_suits) else 0
            self._encoded_vector[4] = 1 if all(matching_suits) else 0
        
    def _encode_bets(self, player_id, action_record):
        for round_number, round_action in enumerate(self._infer_actions(action_record)):
            # Convert number of bets into a binary representation with 3 bits
            raise_count_binary_string = bin(round_action["raise_count"])[2:]
            raise_count_binary = [int(x) for x in raise_count_binary_string]  # Thanks to mgilson @ https://stackoverflow.com/a/13557953/9041692
            for _ in range(3 - len(raise_count_binary)):
                raise_count_binary.insert(0, 0)  # Forces the binary to have 3 bits
            index_offset = 9 + (round_number * 4)
            last_better_was_opponent = 1 if round_action['last_better'] is not None and round_action['last_better'] != player_id else 0
            self._encoded_vector[index_offset] = raise_count_binary[0]
            self._encoded_vector[index_offset + 1] = raise_count_binary[1]
            self._encoded_vector[index_offset + 2] = raise_count_binary[2]
            self._encoded_vector[index_offset + 3] = last_better_was_opponent

    @staticmethod
    def _infer_actions(action_record):
        # While action_record doesn't state when a new round of betting starts,
        # given the 2-player structure of the game this can be inferred.
        # Read the following post for more information:
        # https://github.com/jake-bickle/rlcard/issues/11#issuecomment-660538937
        round_actions = [{'raise_count': 0, 'last_better': None} for _ in range(4)]
        round_number = 0
        new_round = True
        for action in action_record:
            if round_number == 4:
                break
            if action[1] == 'raise':
                round_actions[round_number]['raise_count'] += 1
                round_actions[round_number]['last_better'] = action[0]
                new_round = False
            elif new_round:
                new_round = False
            else:
                # The round is over
                new_round = True
                round_number += 1
        return round_actions

class NoHoleEncoder(LimitHoldemInfosetEncoder):
    '''
        This infoset encoder removes the hole information from LimitHoldemInfoSetEncoder,
        leaving all other bits intact.
    '''
    def encode(self, *args, **kwargs):
        encoded_vector = super().encode(*args, **kwargs)
        indices_to_delete = [i for i in range(25, 25 + self.amount_of_ranks)]  # Remove hole card rank info
        indices_to_delete.extend([0, 2, 4, 6, 8])  # Remove flush information related to hole cards
        return np.delete(encoded_vector, indices_to_delete)

class NoFlushEncoder:
    '''
        Abstracted gamestate encoder that removes suit information from 
        encoding. 
        bit 0: player position (0 = smallblind, 1 = bigblind)
        bit 1-+ranksize: hole cards
        bit +1-+ranksize: flop cards (0s if preflop)
        bit +1: if pair on flop, active if pair is higher rank 
        bit +1-+ranksize: turn card
        bit +1-+ranksize: river card
        bit +1-+5: #bet in current round
        bit +1: player now facing bet?
        bit +1: at least 3 bets preflop
        bit +1: opp bet or raised on flop
        bit +1: opp bet or raised on turn
    '''
    RANK_ORDER = '23456789TJQKA' 
    
    def __init__(self):
        self.amount_of_ranks = len(self.RANK_ORDER)
        self.state_size = 11 + self.amount_of_ranks * 4
        self.state_shape = [self.state_size]
        self._encoded_vector = None

    def encode(self, player_state, action_record):
        '''
            Encodes the player state and action record into a binary list info set.
            Refer to the following post for more information:
            https://github.com/jake-bickle/rlcard/issues/11#issuecomment-661328769

            Args:
                player_state (dict): The dict returned by player.get_state()
                action_record (2D array): An array of actions, where an action is an array [player_id, action_string]

            Returns:
                A binary list of the encoded info set
        '''
        self._encoded_vector = np.zeros(self.state_size)
        self._encode_card_ranks(player_state)
        self._encode_bets(player_state['player_id'], action_record)
        return self._encoded_vector

    def _encode_card_ranks(self, player_state):
        def encode_round_ranks(cards, starting_index):
            for card in cards:
                rank = card[1]
                index = starting_index + self.RANK_ORDER.index(rank)
                if index is not None:
                    self._encoded_vector[index] = 1

        hole_cards = player_state['hand']
        flop_cards = sorted(player_state['public_cards'][:3])
        turn_cards = player_state['public_cards'][3:4]
        river_cards = player_state['public_cards'][4:5]
        encode_round_ranks(hole_cards, 1)
        encode_round_ranks(flop_cards, 1 + self.amount_of_ranks)
        encode_round_ranks(turn_cards, 2 + self.amount_of_ranks * 2)
        encode_round_ranks(river_cards, 2 + self.amount_of_ranks * 3)
        # If there is a pair in the flop, set 1 if the pair is the higher of the two ranks
        if flop_cards and flop_cards[1][1] != flop_cards[0][1] and flop_cards[1][1] == flop_cards[2][1]:
            self._encoded_vector[1 + self.amount_of_ranks * 2] = 1

        
    def _encode_bets(self, player_id, action_record):
        
        if len(action_record) == 0:
            return
        
        self._encoded_vector[0] = abs(action_record[0][0] - player_id)
        offset = 2 + self.amount_of_ranks * 4
        
        round_actions = [{'raise_count': 0, 'last_better': None} for _ in range(4)]
        round_number = 0
        new_round = True
        for action in action_record:
            if round_number == 4:
                break           
            if action[1] == 'raise':
                round_actions[round_number]['raise_count'] += 1
                round_actions[round_number]['last_better'] = action[0]
                new_round = False
                if round_number == 1 and abs(player_id - action[0]) == 1:
                    self._encoded_vector[offset + 7] = 1     
                if round_number == 2 and abs(player_id - action[0]) == 1:
                    self._encoded_vector[offset + 8] = 1     
                                        
            elif new_round:
                new_round = False
            else:
                # The round is over
                new_round = True
                round_number += 1

        cur_bets = round_actions[-1]['raise_count']
        self._encoded_vector[offset + cur_bets] = 1
        if round_actions[-1]['last_better'] not in [None, player_id]:
            self._encoded_vector[offset + 5] = 1
        if round_actions[0]['raise_count'] >= 3:
            self._encoded_vector[offset + 6] = 1

    @staticmethod
    def _infer_actions(action_record):
        # While action_record doesn't state when a new round of betting starts,
        # given the 2-player structure of the game this can be inferred.
        # Read the following post for more information:
        # https://github.com/jake-bickle/rlcard/issues/11#issuecomment-660538937
        round_actions = [{'raise_count': 0, 'last_better': None} for _ in range(4)]
        round_number = 0
        new_round = True
        for action in action_record:
            if round_number == 4:
                break
            if action[1] == 'raise':
                round_actions[round_number]['raise_count'] += 1
                round_actions[round_number]['last_better'] = action[0]
                new_round = False
            elif new_round:
                new_round = False
            else:
                # The round is over
                new_round = True
                round_number += 1
        return round_actions
