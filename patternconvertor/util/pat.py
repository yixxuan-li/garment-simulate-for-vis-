categories = ['no_sleeve_shirt', 'short_sleeve_shirt', 'long_sleeve_shirt', 'long_pants', 'short_pants', 'no_sleeve_dress', 'short_sleeve_dress', 'long_sleeve_dress', 'trumpet_skirt']

indic = {
    'no_sleeve_shirt': {
        'all': slice(0, 44),
        'Body_Front': slice(0, 22),   # 11
        'Body_Back': slice(22, 44),   # 11
    },
    'short_sleeve_shirt': {
        'all': slice(0, 66),
        'Body_Front': slice(0, 22),   # 11
        'Body_Back': slice(22, 44),   # 11
        'Sleeve_Left': slice(44, 66), # 11
    },
    'long_sleeve_shirt': {
        'all': slice(0, 66),
        'Body_Front': slice(0, 22),   # 11
        'Body_Back': slice(22, 44),   # 11
        'Sleeve_Left': slice(44, 66), # 11
    },
    'long_pants': {
        'all': slice(66, 118),
        'Belt': slice(66, 74),           # 4
        'Leg_Left_Front': slice(74, 96), # 11
        'Leg_Left_Back': slice(96, 118), # 11
    },
    'short_pants': {
        'all': slice(66, 118),
        'Belt': slice(66, 74),           # 4
        'Leg_Left_Front': slice(74, 96), # 11
        'Leg_Left_Back': slice(96, 118), # 11
    },
    'no_sleeve_dress': {
        'all': slice(118, 166),
        'Body_Front': slice(118, 142), # 12
        'Body_Back': slice(142, 166),  # 12
    },
    'short_sleeve_dress': {
        'all': slice(118, 188),
        'Body_Front': slice(118, 142), # 12
        'Body_Back': slice(142, 166),  # 12
        'Sleeve_Left': slice(166, 188),# 11
    },
    'long_sleeve_dress': {
        'all': slice(118, 188),
        'Body_Front': slice(118, 142), # 12
        'Body_Back': slice(142, 166),  # 12
        'Sleeve_Left': slice(166, 188),# 11
    },
    'trumpet_skirt': {
        'all': slice(188, 212),
        'Belt_Front': slice(188, 196), # 4
        'Body_Front': slice(196, 212), # 8
    }
}

CLO_SIZE = 212
CAT_NUM = len(categories)
UP = [0, 1, 2]
DOWN = [3, 4, 8]
ALL = [5, 6, 7]
