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
    if declarer == 'N' or declarer == 'S':
        sign = 1
    elif declarer == 'E' or declarer == 'W':
        sign = -1
    else :
        raise ValueError    
    
    # Vulnerability: 0 = non-Vul, 1 = Vul
    vul = 0
    no = int(board_no % 16)
    if no == 4 or no == 7 or no == 10 or no == 13:
        vul = 1
    elif sign == 1 and (no == 2 or no == 5 or no == 12 or no == 15):
        vul = 1
    elif sign == -1 and (no == 3 or no == 6 or no == 9 or no == 0): # 0 = board 16
        vul = 1
	
    score = 0
    if contract == "PASS":
        return score
    
    # Parse contract
    splited_contract = contract.split(' ')
    level = splited_contract[0]
    suit = splited_contract[1]
    if len(splited_contract) == 3:
        penalty = splited_contract[2]
    else:
        penalty = ""
    #print (level, suit, penalty)
    
    # double: 0 = unDbl, 1 = Dbl, 2 = ReDbl
    double = 0 
    if penalty == "x":
        double = 1
    elif penalty == "xx":
        double = 2
    #print ("sign = %d vul = %d double = %d" % (sign, vul, double) )

    # Calculate score 
    
    if result[0] == "-": # down
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
        if suit == "S" or suit == "H":
            score = int(30) * int(level)
        elif suit == "C" or suit == "D":
            score = int(20) * int(level)
        elif suit == "NT":
            score = int(30) * int(level) + int(10)
        else :
            raise ValueError
        #print ("base score = %d" % (score))

        if double > 0:
            score = int(score * double * 2)
        
        # bonus score
        if int(score) < 100: # partial
            score = int(score) + 50
        else: # game
            score = int(score) + 300 + 200 * vul
        #print ("bonus score = %d" % (score))

        if int(level) == 6: # small slam
            score = score + 500 + 250 * vul
        elif int(level) == 7: # grand slam
            score = score + 1000 + 500 * vul

        if double > 0: # dbl-make bonus
            score = score + 50 * double

        # overtrick
        if result[0] == '+':
            overtrick = int(result[1:])
            if double == 0:
                if suit == 'S' or suit == 'H' or  suit == 'NT':
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

def imp_to_vp_compute(imp_diff, board_count):
    diff = abs(imp_diff)
    golden_ratio = ( (5**0.5 - 1) / 2)
    v0 = 10.0
    x = 5 * (board_count**0.5)
    vp = v0 + v0 * (1.0 - golden_ratio**(diff/x)) / ( 1 - golden_ratio**3 )
    vp = round(max(min(vp, 2*v0),0), 2)

    if imp_diff >= 0:
        return vp#, round(2*v0-vp, 2)
    else:
        return round(2*v0-vp, 2)#, vp

def imp_to_vp_lookup_table(imp_diff, board_count):
    table = {
        6:[
            10.00,
            10.50,
            10.99,
            11.46,
            11.90,
            12.33,
            12.75,
            13.15,
            13.53,
            13.90,
            14.25,
            14.59,
            14.92,
            15.24,
            15.54,
            15.83,
            16.11,
            16.38,
            16.64,
            16.89,
            17.12,
            17.35,
            17.58,
            17.79,
            17.99,
            18.19,
            18.38,
            18.56,
            18.73,
            18.90,
            19.06,
            19.22,
            19.37,
            19.51,
            19.65,
            19.78,
            19.91,
            20.00
        ],
        7:[
            10.00,
            10.47,
            10.92,
            11.35,
            11.77,
            12.18,
            12.57,
            12.94,
            13.31,
            13.65,
            13.99,
            14.32,
            14.63,
            14.93,
            15.22,
            15.50,
            15.78,
            16.04,
            16.29,
            16.53,
            16.77,
            16.99,
            17.21,
            17.42,
            17.62,
            17.82,
            18.01,
            18.19,
            18.36,
            18.53,
            18.69,
            18.85,
            19.00,
            19.15,
            19.29,
            19.43,
            19.56,
            19.68,
            19.80,
            19.92,
            20.00
        ],
        8:[
            10.00,
            10.44,
            10.86,
            11.27,
            11.67,
            12.05,
            12.42,
            12.77,
            13.12,
            13.45,
            13.78,
            14.09,
            14.39,
            14.68,
            14.96,
            15.23,
            15.50,
            15.75,
            16.00,
            16.23,
            16.46,
            16.68,
            16.90,
            17.11,
            17.31,
            17.50,
            17.69,
            17.87,
            18.04,
            18.21,
            18.37,
            18.53,
            18.68,
            18.83,
            18.97,
            19.11,
            19.24,
            19.37,
            19.50,
            19.62,
            19.74,
            19.85,
            19.95,
            20.00
        ],
        9:[
            10.00,
            10.41,
            10.81,
            11.20,
            11.58,
            11.94,
            12.29,
            12.63,
            12.96,
            13.28,
            13.59,
            13.89,
            14.18,
            14.46,
            14.74,
            15.00,
            15.26,
            15.50,
            15.74,
            15.97,
            16.20,
            16.42,
            16.63,
            16.83,
            17.03,
            17.22,
            17.41,
            17.59,
            17.76,
            17.93,
            18.09,
            18.25,
            18.40,
            18.55,
            18.69,
            18.83,
            18.97,
            19.10,
            19.22,
            19.34,
            19.46,
            19.58,
            19.69,
            19.80,
            19.90,
            20.00,
        ],
        10:[
            10.00,
            10.39,
            10.77,
            11.14,
            11.50,
            11.85,
            12.18,
            12.51,
            12.83,
            13.14,
            13.43,
            13.72,
            14.00,
            14.28,
            14.54,
            14.80,
            15.05,
            15.29,
            15.52,
            15.75,
            15.97,
            16.18,
            16.39,
            16.59,
            16.78,
            16.97,
            17.16,
            17.34,
            17.51,
            17.68,
            17.84,
            18.00,
            18.15,
            18.30,
            18.44,
            18.58,
            18.71,
            18.84,
            18.97,
            19.10,
            19.22,
            19.33,
            19.44,
            19.55,
            19.66,
            19.76,
            19.86,
            19.96,
            20.00,
        ],
        11:[
            10.00,
            10.36,
            10.71,
            11.05,
            11.38,
            11.70,
            12.01,
            12.31,
            12.61,
            12.90,
            13.18,
            13.45,
            13.71,
            13.97,
            14.22,
            14.46,
            14.70,
            14.93,
            15.15,
            15.37,
            15.58,
            15.79,
            15.99,
            16.18,
            16.37,
            16.55,
            16.73,
            16.91,
            17.08,
            17.24,
            17.40,
            17.56,
            17.71,
            17.86,
            18.00,
            18.14,
            18.28,
            18.41,
            18.54,
            18.66,
            18.78,
            18.90,
            19.02,
            19.13,
            19.24,
            19.34,
            19.44,
            19.54,
            19.64,
            19.74,
            19.83,
            19.92,
            20.00,
        ],
        12:[
            10.00,
            10.33,
            10.66,
            10.97,
            11.28,
            11.58,
            11.87,
            12.16,
            12.44,
            12.71,
            12.97,
            13.23,
            13.48,
            13.72,
            13.96,
            14.19,
            14.42,
            14.64,
            14.85,
            15.06,
            15.26,
            15.46,
            15.66,
            15.85,
            16.03,
            16.21,
            16.38,
            16.55,
            16.72,
            16.88,
            17.04,
            17.19,
            17.34,
            17.49,
            17.63,
            17.77,
            17.91,
            18.04,
            18.17,
            18.29,
            18.41,
            18.53,
            18.65,
            18.76,
            18.87,
            18.98,
            19.08,
            19.18,
            19.28,
            19.38,
            19.47,
            19.56,
            19.65,
            19.74,
            19.83,
            19.91,
            19.99,
            20.00,
        ],
        16:[
            10.00,
            10.31,
            10.61,
            10.91,
            11.20,
            11.48,
            11.76,
            12.03,
            12.29,
            12.55,
            12.80,
            13.04,
            13.28,
            13.52,
            13.75,
            13.97,
            14.18,
            14.39,
            14.60,
            14.80,
            15.00,
            15.19,
            15.38,
            15.56,
            15.74,
            15.92,
            16.09,
            16.26,
            16.42,
            16.58,
            16.73,
            16.88,
            17.03,
            17.17,
            17.31,
            17.45,
            17.59,
            17.72,
            17.85,
            17.97,
            18.09,
            18.21,
            18.33,
            18.44,
            18.55,
            18.66,
            18.77,
            18.87,
            18.97,
            19.07,
            19.16,
            19.25,
            19.34,
            19.43,
            19.52,
            19.61,
            19.69,
            19.77,
            19.85,
            19.93,
            20.00,
        ],
        20:[
            10.00,
            10.28,
            10.55,
            10.82,
            11.08,
            11.34,
            11.59,
            11.83,
            12.07,
            12.30,
            12.53,
            12.76,
            12.98,
            13.20,
            13.41,
            13.61,
            13.81,
            14.01,
            14.20,
            14.39,
            14.58,
            14.76,
            14.94,
            15.11,
            15.28,
            15.45,
            15.61,
            15.77,
            15.93,
            16.08,
            16.23,
            16.38,
            16.52,
            16.66,
            16.80,
            16.93,
            17.06,
            17.19,
            17.32,
            17.44,
            17.56,
            17.68,
            17.79,
            17.90,
            18.01,
            18.12,
            18.23,
            18.33,
            18.43,
            18.53,
            18.63,
            18.73,
            18.82,
            18.91,
            19.00,
            19.09,
            19.17,
            19.25,
            19.33,
            19.41,
            19.49,
            19.57,
            19.65,
            19.72,
            19.79,
            19.86,
            19.93,
            19.99,
            20.00,
        ],
        32:[
            10.00,
            10.22,
            10.44,
            10.65,
            10.86,
            11.07,
            11.27,
            11.47,
            11.67,
            11.86,
            12.05,
            12.24,
            12.42,
            12.60,
            12.78,
            12.95,
            13.12,
            13.29,
            13.46,
            13.62,
            13.78,
            13.94,
            14.09,
            14.24,
            14.39,
            14.54,
            14.68,
            14.82,
            14.96,
            15.10,
            15.24,
            15.37,
            15.50,
            15.63,
            15.76,
            15.88,
            16.00,
            16.12,
            16.24,
            16.35,
            16.46,
            16.57,
            16.68,
            16.79,
            16.90,
            17.01,
            17.11,
            17.21,
            17.31,
            17.41,
            17.51,
            17.60,
            17.69,
            17.78,
            17.87,
            17.96,
            18.05,
            18.13,
            18.21,
            18.29,
            18.37,
            18.45,
            18.53,
            18.61,
            18.69,
            18.76,
            18.83,
            18.90,
            18.97,
            19.04,
            19.11,
            19.18,
            19.25,
            19.32,
            19.38,
            19.44,
            19.50,
            19.56,
            19.62,
            19.68,
            19.74,
            19.80,
            19.85,
            19.90,
            19.95,
            20.00,
        ]
    }
    if board_count in table:
        if abs(imp_diff) < len(table[board_count]):
            vp = table[board_count][int(abs(imp_diff))]
        else:
            vp = table[board_count][-1]
        if imp_diff >= 0:
            return vp
        else:
            return 20.0-vp
    return None

def imp_to_vp(imp_diff, board_count):
    if board_count in [6,7,8,9,10,12,14,16,20,32]:
        return imp_to_vp_lookup_table(imp_diff, board_count)
    else:
        return imp_to_vp_compute(imp_diff, board_count)
