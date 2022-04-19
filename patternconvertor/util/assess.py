import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from clo.pattern import Polygon

class Assess(object):
    INIT = -1
    OK = 1
    RUN = 2
    SKIP = 3
    LOOP = 4

class AssessPlot(object):
    """AssessPlot class used for assess the fitting answer is perfect or not

    Attributes:
        s: assessment result
    """
    def __init__(self) -> None:
        self.s = Assess.INIT

    def ok(self, event):
        self.s = Assess.OK
        plt.close()

    def run(self, event):
        self.s = Assess.RUN
        plt.close()

    def skip(self, event):
        self.s = Assess.SKIP
        plt.close()
    
    def loop(self, event):
        self.s = Assess.LOOP
        plt.close()
    
    def showAnswer(self, s: Polygon, t: Polygon, ok: bool = True, run: bool = True, skip: bool = True, loop: bool = True):
        """Show the compared answer

        Args:
            s: source polygon object
            t: target polygon object
            ok: show ok button or not
            run: show rerun button or not
            skip: show skip button or not
            loop: show loop button or not
        
        Return:
            the assessment result
        """
        plt.axis("equal")
        s.draw(plt, color='r')
        t.draw(plt, color='k')
        if ok:
            buttonOK = Button(plt.axes([0.6, 0.00, 0.05, 0.05]), 'Ok', color='khaki')
            buttonOK.on_clicked(self.ok)
        if run:
            buttonRerun = Button(plt.axes([0.5, 0.00, 0.07, 0.05]), 'Rerun', color='khaki')
            buttonRerun.on_clicked(self.run)
        if skip:
            buttonSkip = Button(plt.axes([0.4, 0.00, 0.05, 0.05]), 'Skip', color='khaki')
            buttonSkip.on_clicked(self.skip)
        if loop:
            buttonLoop = Button(plt.axes([0.3, 0.00, 0.05, 0.05]), 'Loop', color='khaki')
            buttonLoop.on_clicked(self.loop)
        plt.show()
        return self.s

class VertexByHandPlot(object):
    """ VertexByHandPlot used for modify vertex position by hand """
    def __init__(self):
        self.pos = None

    def onclick(self, event):
        self.pos = [event.xdata, event.ydata]
        print('click pos: ', self.pos)

    def showAnswer(self, s: Polygon, t: Polygon,):
        """ This is used for correct vertex by hand

        Args:
            s: source polygon
            t: target polygon
        """
        fig = plt.figure()
        plt.axis("equal")
        plt.title('Correct Vertex by Hand',color='red')
        s.draw(plt, color='r')
        t.draw(plt, color='k')
        cid = fig.canvas.mpl_connect('button_press_event', self.onclick)

        plt.show()
        return self.pos

def show_compare(source: Polygon, target: Polygon) -> None:
    """Compare source and target pattern with graphic

    Args:
        source: source pattern
        target: target pattern
    """
    plt.axis("equal")
    source.draw(plt, color='r')
    target.draw(plt, color='k')
    plt.figure
    plt.show()
    plt.cla()