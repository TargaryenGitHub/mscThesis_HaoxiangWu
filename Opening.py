from shapely.geometry import Point



class Door(object):
    def __init__(self, mline, width, length):
        self.mline = mline
        self.width = width
        self.center = Point((list(mline.coords)[0][0]+list(mline.coords)[1][0])/2, (list(mline.coords)[0][1]+list(mline.coords)[1][1])/2)
        self.type = 0 # 0 is door
        self.length = length
      
      
class Window(object):
    def __init__(self, mline, width, length):
        self.mline = mline
        self.width = width
        self.center = Point((list(mline.coords)[0][0]+list(mline.coords)[1][0])/2, (list(mline.coords)[0][1]+list(mline.coords)[1][1])/2)
        self.type = 1 # 1 is window
        self.length = length
