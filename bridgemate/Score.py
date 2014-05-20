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
