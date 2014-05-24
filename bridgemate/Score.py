def compute_score(board_no, contract, declarer, result):
    # contract = t c x (t = 1-7, c = C/D/H/S/NT, x = x/xx)
    #        ex. 1 H
    #            2 NT
    #            4 S x
    #            3 D xx
    #            PASS
    # declarer = N E S W
    # result = -13 ... -1 = +1 ... +6

    # NS win: plus, EW win: minus
    sign = 0
    if declarer == 'N' or 'S':
        sign = 1
    elif declarer == 'E' or 'W':
        sign = -1
    else raise ValueError
    
    # Vulnerability: 0 = non-Vul, 1 = Vul
    vul = 0
    no = board_no % 16
    if no == 4 or 7 or 10 or 13:
        vul = 1
    elif sign == 1 and no == 2 or 5 or 12 or 15:
        vul = 1
    elif sign == -1 and no == 3 or 6 or 9 or 0: # 0 = board 16
        vul = 1
	
    # Parse contract
    level, suit, penalty = contract.split(' ')
    
    # double: 0 = unDbl, 1 = Dbl, 2 = ReDbl
    double = 0 
    if penalty == 'x':
        double = 1
    elif penalty == 'xx':
        double = 2

    # Calculate score
    score = 0 
    if result == 'PASS':
        return score
    
    if result[0] == '-': # down
        undertrick = int(result[1:])
        if double == 0:
            if vul == 0:
                score = -50 * undertrick
            else:
                score = -100 * undertrick
        else: # doubled
            if vul == 0:
                if undertrick <= 3:
                    score = (-200 * undertrick + 100) * double
                else:
                    score = (-500 - (undertrick - 3) * 300 ) * double
            else:
                score = (-300 * undertrick + 100) * double

    else: # make
        # base score
        if suit == 'S' or 'H':
            score = 30 * level
        elif suit == 'C' or 'D':
            score = 20 * level
        elif suit = 'NT':
            score = 30 * level + 10
        else raise ValueError

        if double > 0:
            score = score * double * 2
        
        # bonus score
        if score < 100: # partial
            score = score + 50
        else: # game
            score = score + 300 + 200 * vul

        if level == 6: # small slam
            score = score + 500 + 250 * vul
        elif level == 7: # grand slam
            score = score + 1000 + 500 * vul

        if double > 0: # dbl-make bonus
            score = score + 50 * double

        # overtrick
        if result[0] == '+':
            overtrick = int(result[1:])
            if double == 0:
                if suit == 'S' or 'H' or 'NT':
                    score = score + 30 * overtrick
                else:
                    score = score + 20 * overtrick
            else:
                score = score + (100 + 100 * vul) * double * overtrick
        
    
    score = score * sign # negate if declared by EW
    
    return score


def score_to_imp(score_a, score_b):
    imp_tables = [
        #               imp
        (0,     20,     0),
        (20,    50,     1),
        (50,    90,     2),
        (90,    130,    3),
        (130,   170,    4),
        (170,   220,     5),
        (220,   270,     6),
        (270,   320,     7),
        (320,   370,     8),
        (370,   430,     9),
        (430,   500,     10),
        (500,   600,     11),
        (600,   750,     12),
        (750,   900,     13),
        (900,  1100,     14),
        (1100, 1300,     15),
        (1300, 1500,     16),
        (1500, 1750,     17),
        (1750, 2000,     18),
        (2000, 2250,     19),
        (2250, 2500,     20),
        (2500, 3000,     21),
        (3000, 3500,     22),
        (3500, 4000,     23),
        (4000, 1000000000000,     24),
    ]

    diff = abs(score_a-score_b)
    sign = 1 if score_a >= score_b else -1

    for low, up, imp in imp_tables:
        if diff >= low and diff < up:
            return sign * imp

    return None

def imp_to_vp(imp_diff, board_count):
    diff = abs(imp_diff)
    golden_ratio = ( (5**0.5 - 1) / 2)
    v0 = 10.0
    x = 5 * (board_count**0.5)
    vp = v0 + v0 * (1.0 - golden_ratio**(diff/x)) / ( 1 - golden_ratio**3 )
    vp = round(max(min(vp, 2*v0),0), 2)

    if imp_diff >= 0:
        return vp, round(2*v0-vp, 2)
    else:
        return round(2*v0-vp, 2), vp
