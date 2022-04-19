from clo.pattern import *
from util.pat import indic, categories


class Garment(object):
    def __init__(self):
        self.pattern = []
    
    def load_points(self, points, cat_name):
        for i in range(len(self.pattern)):
            pat_name = self.pattern[i].name
            slc = indic[cat_name][pat_name]

            self.pattern[i].resetPoints(points[slc].reshape(-1, 2))

    def load_points_dict(self, points):
        for i in range(len(self.pattern)):
            pat_num = self.pattern[i].name
            if pat_num not in points:
                raise Exception('No {} pattern in points dict.'.format(pat_num))
            
            self.pattern[i].resetPoints(points[pat_num])

class No_Sleeve_Shirt(Garment):
    def __init__(self):
        self.pattern = []
        self.pattern.append(Shirt_Body_Front(points=None))
        self.pattern.append(Shirt_Body_Back(points=None))
        
        self.points_num = 0
        for pat in self.pattern:
            self.points_num += len(pat.points)
        
        self.seam = [
            [[(0, 1)], [(1, 1)]],
            [[(0, 3)], [(1, 3)]],
        ]

class Short_Sleeve_Shirt(Garment):
    def __init__(self):
        self.pattern = []
        self.pattern.append(Shirt_Body_Front(points=None))
        self.pattern.append(Shirt_Body_Back(points=None))
        self.pattern.append(Shirt_Sleeve(points=None))
        
        self.points_num = 0
        for pat in self.pattern:
            self.points_num += len(pat.points)
        
        self.seam = [
            [[(0, 1)], [(1, 1)]],
            [[(0, 3)], [(1, 3)]],
            [[(0, 2), (1, 2)], [(2, 3), (2, 4)]] # seam (pattern 0, line 2) + (pattern 1, line 2) <---> (pattern 2, line 3) + (pattern 2, line 4)
        ]

class Long_Sleeve_Shirt(Garment):
    def __init__(self):
        self.pattern = []
        self.pattern.append(Shirt_Body_Front(points=None))
        self.pattern.append(Shirt_Body_Back(points=None))
        self.pattern.append(Shirt_Sleeve(points=None))
        
        self.points_num = 0
        for pat in self.pattern:
            self.points_num += len(pat.points)
        
        self.seam = [
            [[(0, 1)], [(1, 1)]],
            [[(0, 3)], [(1, 3)]],
            [[(0, 2), (1, 2)], [(2, 3), (2, 4)]] # seam (pattern 0, line 2) + (pattern 1, line 2) <---> (pattern 2, line 3) + (pattern 2, line 4)
        ]

class Trumpet_Skirt(Garment):  
    def __init__(self):
        self.pattern = []
        self.pattern.append(Trumpet_Skirt_Belt(points=None))
        self.pattern.append(Trumpet_Skirt_Body(points=None))

        self.points_num = 0
        for pat in self.pattern:
            self.points_num += len(pat.points)
        
        self.seam = [
            [[(0, 0)], [(1, 2)]]
        ]

class Long_Pants(Garment):
    def __init__(self):
        self.pattern = []
        self.pattern.append(Pants_Belt(points=None))
        self.pattern.append(Pants_Left_Front(points=None))
        self.pattern.append(Pants_Left_Back(points=None))

        self.points_num = 0
        for pat in self.pattern:
            self.points_num += len(pat.points) 
        
        self.seam = [
            [[(1, 1)], [(2, 2)]], # seam 1, (pattern 1, line 1) <---> (pattern 2, line 2) 
            [[(1, 3)], [(2, 0)]], # seam 2, (pattern 1, line 3) <---> (pattern 2, line 0)
        ]

class Short_Pants(Garment):
    def __init__(self):
        self.pattern = []
        self.pattern.append(Pants_Belt(points=None))
        self.pattern.append(Pants_Left_Front(points=None))
        self.pattern.append(Pants_Left_Back(points=None))

        self.points_num = 0
        for pat in self.pattern:
            self.points_num += len(pat.points)
        
        self.seam = [
            [[(1, 1)], [(2, 2)]], # seam 1, (pattern 1, line 1) <---> (pattern 2, line 2) 
            [[(1, 3)], [(2, 0)]], # seam 2, (pattern 1, line 3) <---> (pattern 2, line 0)
        ]

class No_Sleeve_Dress(Garment):
    def __init__(self):
        self.pattern = []
        self.pattern.append(Dress_Body_Front(points=None))
        self.pattern.append(Dress_Body_Back(points=None))

        self.points_num = 0
        for pat in self.pattern:
            self.points_num += len(pat.points)
        
        self.seam = [
            [[(0, 1)], [(1, 1)]], 
            [[(0, 3)], [(1, 3)]] # seam 2, (pattern 0, line 3) <---> (pattern 1, line 3)
        ]

class Short_Sleeve_Dress(Garment):
    def __init__(self):
        self.pattern = []
        self.pattern.append(Dress_Body_Front(points=None))
        self.pattern.append(Dress_Body_Back(points=None))
        self.pattern.append(Shirt_Sleeve(points=None))

        self.points_num = 0
        for pat in self.pattern:
            self.points_num += len(pat.points)
        
        self.seam = [
            [[(0, 1)], [(1, 1)]], 
            [[(0, 3)], [(1, 3)]], # seam 2, (pattern 0, line 3) <---> (pattern 1, line 3)
            [[(0, 2), (1, 2)], [(2, 3), (2, 4)]]
        ]

class Long_Sleeve_Dress(Garment):
    def __init__(self):
        self.pattern = []
        self.pattern.append(Dress_Body_Front(points=None))
        self.pattern.append(Dress_Body_Back(points=None))
        self.pattern.append(Shirt_Sleeve(points=None))

        self.points_num = 0
        for pat in self.pattern:
            self.points_num += len(pat.points)
        
        self.seam = [
            [[(0, 1)], [(1, 1)]], 
            [[(0, 3)], [(1, 3)]], # seam 2, (pattern 0, line 3) <---> (pattern 1, line 3)
            [[(0, 2), (1, 2)], [(2, 3), (2, 4)]]
        ]

CLOTH = {
    'no_sleeve_shirt': lambda : No_Sleeve_Shirt(),
    'short_sleeve_shirt': lambda : Short_Sleeve_Shirt(),
    'long_sleeve_shirt': lambda : Long_Sleeve_Shirt(),
    'trumpet_skirt': lambda : Trumpet_Skirt(),
    'long_pants': lambda: Long_Pants(),
    'short_pants': lambda : Short_Pants(),
    'no_sleeve_dress': lambda: No_Sleeve_Dress(),
    'short_sleeve_dress': lambda: Short_Sleeve_Dress(),
    'long_sleeve_dress': lambda: Long_Sleeve_Dress()
}