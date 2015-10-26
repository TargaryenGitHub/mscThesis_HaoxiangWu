from shapely.geometry import LineString
from shapely.geometry import Point
from angle_of_line import angle_of_line
import math
import time
import fiona
from collections import OrderedDict


def find_intersectingPoint(l1, l2):
    # find intersecting point of two unparallel lines
    x11=list(l1.coords)[0][0]
    y11=list(l1.coords)[0][1]
    x12=list(l1.coords)[1][0]
    y12=list(l1.coords)[1][1]
    
    x21=list(l2.coords)[0][0]
    y21=list(l2.coords)[0][1]
    x22=list(l2.coords)[1][0]
    y22=list(l2.coords)[1][1]
    
    A1=y12-y11
    B1=x11-x12
    C1=x12*y11-x11*y12
    
    A2=y22-y21
    B2=x21-x22
    C2=x22*y21-x21*y22
    
    x0=(-1)*(B2*C1-B1*C2)/(A1*B2-A2*B1)
    y0=(-1)*(A2*C1-A1*C2)/(A2*B1-A1*B2)
    
    return Point(x0, y0)

def fix_disjoint_vertices(l1, l2):
    a1=angle_of_line(l1)
    a2=angle_of_line(l2)
    if math.fabs(a1-a2)<=2:
        return []

    else:
        if l1.intersects(l2)==True:
            pt=l1.intersection(l2)
            return [(pt.x, pt.y)]

        else:
            pt=find_intersectingPoint(l1, l2)
            return [(pt.x, pt.y)]
            


def fix_duplicated_lines(lines, MINIMALDIST):

    
    new_lines=[]
    while len(lines)>0:     
        print len(lines),len(new_lines)
        
        l1=lines[0]
        
        if l1.length<MINIMALDIST:
            print 'Null-length'
            lines.pop(0)
            continue
        
        if len(lines)==0:
            break
        elif len(lines)==1:
            new_lines.append(l1)
            lines.pop(0)
            break
        else:

            for i in range(1, len(lines)+1):
                
                if i==len(lines):
                    new_lines.append(l1)
                    lines.pop(0)
                    break
                    
                l2=lines[i]
                if l2.length<MINIMALDIST:
                    print 'Null-length'
                    lines.pop(i)
                    break                    
                a1=angle_of_line(l1)
                a2=angle_of_line(l2)
                if math.fabs(a1-a2)<=2:
                    bff=l1.buffer(MINIMALDIST, resolution=16, cap_style=2)
                    if bff.intersects(l2)==True:
                        if bff.exterior.intersection(l2).geom_type=='GeometryCollection':
                            # contains
                            lines.pop(i)
                            print 'Contains'
                            break
                        elif bff.exterior.intersection(l2).geom_type=='Point':
                            # overlapped or consecutive
                            pt11=Point(list(l1.coords)[0])
                            pt12=Point(list(l1.coords)[1])
                            pt21=Point(list(l2.coords)[0])
                            pt22=Point(list(l2.coords)[1])
                            if pt21.intersects(bff)==True:
                                if pt22.distance(pt11)>=pt22.distance(pt12):
                                    nl=LineString([(pt11.x, pt11.y), (pt22.x, pt22.y)])
                                else:
                                    nl=LineString([(pt12.x, pt12.y), (pt22.x, pt22.y)])
                            else:
                                if pt21.distance(pt11)>=pt21.distance(pt12):
                                    nl=LineString([(pt11.x, pt11.y), (pt21.x, pt21.y)])
                                else:
                                    nl=LineString([(pt12.x, pt12.y), (pt21.x, pt21.y)])
                            lines.pop(i)
                            lines.pop(0)
                            lines.append(nl)
                            print 'Overlapped or Consecutive'
                            break
                        elif bff.exterior.intersection(l2).geom_type=='MultiPoint':
                            # contained
                            lines.pop(0)
                            print 'Contained'
                            break


    return new_lines  
        
        
        
#        i=0
#        while True:
#            
#            if i==len(lines):
#                new_lines.append(l1)
#                break
#        
#            l2=lines[i]
#            a1=angle_of_line(l1)
#            a2=angle_of_line(l2)
#            if math.fabs(a1-a2)<=2:
#                # check if parallel
#                bff=l1.buffer(MINIMALDIST, resolution=16, cap_style=2)
#                if bff.intersects(l2)==True:
#                    # check if closed enough
##                    print bff.exterior.intersection(l2).geom_type
#                    if bff.exterior.intersection(l2).geom_type=='GeometryCollection':
#                        # contains
#                        lines.pop(i)
#                        print 'contains',len(lines),len(new_lines)
#                        break
#                    
#                    elif bff.exterior.intersection(l2).geom_type=='Point':
#                        # overlapped or consecutive
#                        pt11=Point(list(l1.coords)[0])
#                        pt12=Point(list(l1.coords)[1])
#                        pt21=Point(list(l2.coords)[0])
#                        pt22=Point(list(l2.coords)[1])
#                        if pt21.intersects(bff)==True:
#                            if pt22.distance(pt11)>=pt22.distance(pt12):
#                                nl=LineString([(pt11.x, pt11.y), (pt22.x, pt22.y)])
#                            else:
#                                nl=LineString([(pt12.x, pt12.y), (pt22.x, pt22.y)])
#                        else:
#                            if pt21.distance(pt11)>=pt21.distance(pt12):
#                                nl=LineString([(pt11.x, pt11.y), (pt21.x, pt21.y)])
#                            else:
#                                nl=LineString([(pt12.x, pt12.y), (pt21.x, pt21.y)])
#                        
#                        lines.pop(i)
#                        lines.append(nl)
#                        print 'overlapped or consecutive',len(lines),len(new_lines)
#                        break
#                        
#                    elif bff.exterior.intersection(l2).geom_type=='MultiPoint':
#                        # contained
#                        print 'contained',len(lines),len(new_lines) 
#                        break
#                                           
#                else:
#                    i=i+1                    
#            else:
#                i=i+1
#    return new_lines        
