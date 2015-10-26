from shapely.geometry import Point
from shapely.geometry import LineString 
from shapely.geometry import Polygon
import dxfgrabber
import fiona
import math
from collections import OrderedDict

def left_right_line(startpoint, endpoint, pt):
    x1=startpoint.x
    y1=startpoint.y
    x2=endpoint.x
    y2=endpoint.y
    x3=pt.x
    y3=pt.y
    S=(x1-x3)*(y2-y3)-(y1-y3)(x2-x3)
    if S>0:
        # on the left
        return 1
    else:
        # on the right
        return -1


def point_on_line(endpoint, startpoint, l):
    x1=endpoint.x
    y1=endpoint.y
    x2=startpoint.x
    y2=startpoint.y
    
    if x1==x2:
        if y1>y2:
            x3=x2
            y3=y2+l
        else:
            x3=x2
            y3=y2-l
        return Point(x3,y3)
    
    if y1==y2:
        if x1>x2:
            x3=x2+l
            y3=y2
        else:
            x3=x2-l
            y3=y2
        return Point(x3,y3)

    if x1>x2:
        
        if y1>y2:
            x3=x2+l/math.sqrt(1+math.pow((y2-y1)/(x2-x1), 2))
            y3=y2+l/math.sqrt(1+math.pow((x2-x1)/(y2-y1), 2))
        else:
            x3=x2+l/math.sqrt(1+math.pow((y2-y1)/(x2-x1), 2))
            y3=y2-l/math.sqrt(1+math.pow((x2-x1)/(y2-y1), 2))
        
        return Point(x3,y3)
        
    else:
        
        if y1>y2:
            x3=x2-l/math.sqrt(1+math.pow((y2-y1)/(x2-x1), 2))
            y3=y2+l/math.sqrt(1+math.pow((x2-x1)/(y2-y1), 2))
        else:
            x3=x2-l/math.sqrt(1+math.pow((y2-y1)/(x2-x1), 2))
            y3=y2-l/math.sqrt(1+math.pow((x2-x1)/(y2-y1), 2))
        
        return Point(x3,y3)


def extend_line_onedir(endpoint, startpoint, l):
    x1=endpoint.x
    y1=endpoint.y
    x2=startpoint.x
    y2=startpoint.y
    
    if x1==x2:
        if y1>y2:
            x3=x1
            y3=y1+l
        else:
            x3=x1
            y3=y1-l
        return Point(x3,y3)
    
    if y1==y2:
        if x1>x2:
            x3=x1+l
            y3=y1
        else:
            x3=x1-l
            y3=y1
        return Point(x3,y3)

    if x1>x2:
        
        if y1>y2:
            x3=x1+l/math.sqrt(1+math.pow((y2-y1)/(x2-x1), 2))
            y3=y1+l/math.sqrt(1+math.pow((x2-x1)/(y2-y1), 2))
        else:
            x3=x1+l/math.sqrt(1+math.pow((y2-y1)/(x2-x1), 2))
            y3=y1-l/math.sqrt(1+math.pow((x2-x1)/(y2-y1), 2))
        
        return Point(x3,y3)
        
    else:
        
        if y1>y2:
            x3=x1-l/math.sqrt(1+math.pow((y2-y1)/(x2-x1), 2))
            y3=y1+l/math.sqrt(1+math.pow((x2-x1)/(y2-y1), 2))
        else:
            x3=x1-l/math.sqrt(1+math.pow((y2-y1)/(x2-x1), 2))
            y3=y1-l/math.sqrt(1+math.pow((x2-x1)/(y2-y1), 2))
        
        return Point(x3,y3)
#------------------------------------------------------------------------------
        
def extend_line_bothdir(p1, p2, l):
    return [extend_line_onedir(p1, p2, l), extend_line_onedir(p2, p1, l)]
    
    
    
    
#------------------------------------------------------------------------------
        
        
        

if __name__ == "__main__":
    p2=Point(-100,80)
    p1=Point(10,20)
    l=50
    result=extend_line_bothdir(p1, p2, l)
    p3=result[0]
    p4=result[1]
    l1=LineString([(p1.x,p1.y), (p2.x,p2.y)])
    l2=LineString([(p3.x,p3.y), (p4.x,p4.y)])
    
    
    
    
        
#------------------------------------------------------------------------------
    with fiona.open('only_walls.shp') as source:
        source_driver = source.driver
        source_crs = source.crs
        source_schema = source.schema    
    
    
        
        with fiona.open('l1.shp', 'w', crs=source_crs, driver=source_driver, schema=source_schema,) as c:
            
            coordinates=list(l1.coords)
            rec = {'geometry':{'coordinates':coordinates, 
                               'type': 'LineString'},
                   'id': str(0),
                   'properties': OrderedDict([(u'myid', str(0))]),
                   'type': 'Feature'}               
            c.write(rec)

        c.close()
    
        with fiona.open('l2.shp', 'w', crs=source_crs, driver=source_driver, schema=source_schema,) as c:
            
            coordinates=list(l2.coords)
            rec = {'geometry':{'coordinates':coordinates, 
                               'type': 'LineString'},
                   'id': str(0),
                   'properties': OrderedDict([(u'myid', str(0))]),
                   'type': 'Feature'}               
            c.write(rec)

        c.close()
