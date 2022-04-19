import pickle
import random
import numpy as np

from util.pat import indic, categories, CLO_SIZE
from clo.cloth import CLOTH

def vis_pat(cat_name, d):

    import matplotlib.pyplot as plt
    gar = CLOTH[cat_name]()
    gar.load_points(d[:CLO_SIZE], cat_name)

    pat_num = len(gar.pattern)
    for i,p in enumerate(gar.pattern):
        plt.subplot(pat_num, 1, i + 1)
        plt.axis("equal")
        plt.title(cat_name + " - " + p.name, color='red')

        gar.pattern[i].draw(plt)
    
    plt.savefig("tmp.png")