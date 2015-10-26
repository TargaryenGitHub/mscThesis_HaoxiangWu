import math
import shapefile

from shapely.geometry import Point
from shapely.geometry import LineString 
from shapely.geometry import Polygon
from shapely.geometry import polygon

from untitled0 import GetProjectivePoint
from untitled0 import separate_in_out

from extend_line import extend_line_onedir
from extend_line import extend_line_bothdir
from extend_line import point_on_line


def ContourReconstruction00(groupedPoints, openings, AVG_WALL_THICKNESS, verbose):
    
    Nodes=[]
    groups_P=groupedPoints
    for i in range(0, len(openings)):
        l1=openings[i].mline
        width=openings[i].width
        anchor_lines=[]
                
        for j in range(0, len(groups_P)):
            for k in range(0, len(groups_P[j])):
                if k==len(groups_P[j])-1:
                    l2=LineString([groups_P[j][k], groups_P[j][0]])
                else:
                    l2=LineString([groups_P[j][k], groups_P[j][k+1]])
    
                if l1.intersects(l2)==True:
                    anchor_lines.append([j, k, l2])
                    
            if len(anchor_lines)==2:
                break
            else:
                continue
            
        if j==len(groups_P)-1 and len(anchor_lines)<2:
            print 'Opening ' + str(i) +' reconstruction failed!'
            continue
        else:
            
            # openings that can be successfully reconstructed
            Nodes.append(openings[i])
                
            if anchor_lines[0][2].length>=anchor_lines[1][2].length:
                longL=anchor_lines[0]
                shortL=anchor_lines[1]
            else:
                longL=anchor_lines[1]
                shortL=anchor_lines[0] 
                
            if anchor_lines[0][0]==anchor_lines[1][0]:
                # self-closed
                if verbose==True:
                    print 'self-closed'
    
    #------------------------------------------------------------------------------            
                if longL[2].length<=AVG_WALL_THICKNESS:
                    
                    if verbose==True:
                        print 'situation111'
                        
                    if math.fabs(longL[2].length-shortL[2].length)/shortL[2].length<=0.15:            
    #------------------------------------------------------------------------------                    
                        outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                        groups_P.pop(longL[0])  
                        groups_P.append(outRing)
                        groups_P.append(inRing)
    #------------------------------------------------------------------------------  
                        
                    else:
                        outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                     
                        ptProj0=GetProjectivePoint(Point(groups_P[shortL[0]][shortL[1]][0], groups_P[shortL[0]][shortL[1]][1]), longL[2])
                        ptProj1=GetProjectivePoint(Point(groups_P[shortL[0]][shortL[1]+1][0], groups_P[shortL[0]][shortL[1]+1][1]), longL[2])
                        
                        if groups_P[shortL[0]][shortL[1]] in outRing:                    
                            new_outRing=outRing+[(ptProj0.x, ptProj0.y)]
                            new_inRing=[(ptProj1.x, ptProj1.y)]+inRing
                        else:
                            new_outRing=[(ptProj1.x, ptProj1.y)]+outRing
                            new_inRing=inRing+[(ptProj0.x, ptProj0.y)]                    
                         
                        groups_P.pop(longL[0])  
                        groups_P.append(new_outRing)
                        groups_P.append(new_inRing)
    #------------------------------------------------------------------------------                      
                        
                        
                elif shortL[2].length>AVG_WALL_THICKNESS:
                    # self-closed
                    if verbose==True:
                        print 'self-closed222'
                        
                    shortP=l1.intersection(shortL[2])
                    longP=l1.intersection(longL[2])
                    
                    startS=groups_P[shortL[0]][shortL[1]]
                    if shortL[1]+1>=len(groups_P[shortL[0]]):
                        endS=groups_P[shortL[0]][shortL[1]+1-len(groups_P[shortL[0]])]
                    else:
                        endS=groups_P[shortL[0]][shortL[1]+1]
                        
                    startL=groups_P[longL[0]][longL[1]]
                    if longL[1]+1>=len(groups_P[longL[0]]):
                        endL=groups_P[longL[0]][longL[1]+1-len(groups_P[longL[0]])]
                    else:
                        endL=groups_P[longL[0]][longL[1]+1]
    #------------------------------------------------------------------------------               
                    
                    if shortP.distance(Point(startS[0],startS[1]))<=60:
                        if longP.distance(Point(endL[0],endL[0]))<=60:
                            d1=shortP.distance(Point(startS[0],startS[1]))
                            d2=longP.distance(Point(endL[0],endL[0]))
                            
                            if math.fabs(d1-d2)/d1<=0.15:
                                if verbose==True:
                                    print 'U shape(closed)'
                                    
                                # situation 1
                                outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
    
                                new_pt0=point_on_line(Point(endS[0],endS[1]), shortP, (d1+d2)/2)
                                new_pt1=point_on_line(Point(startL[0],startL[1]), longP, (d1+d2)/2)                        
                                
                                new_outRing=outRing
                                new_inRing=[(new_pt0.x,new_pt0.y)]+inRing+[(new_pt1.x,new_pt1.y)]
                                
                                groups_P.pop(longL[0])  
                                groups_P.append(new_outRing)
                                groups_P.append(new_inRing)
                                
                            else:
                                if verbose==True:
                                    print 'U(Z) shape(closed)'
                                    
                                if d1<d2:
                                    ptProj=GetProjectivePoint(Point(startS[0],startS[1]), longL[2])
                                    outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                                    
                                    new_pt0=point_on_line(Point(endS[0],endS[1]), shortP, (d1+d2)/2)
                                    new_pt1=point_on_line(Point(startL[0],startL[1]), longP, (d1+d2)/2) 
            
                                    new_outRing=outRing+[(ptProj.x, ptProj.y)]
                                    new_inRing=[(new_pt0.x,new_pt0.y)]+inRing+[(new_pt1.x,new_pt1.y)]
                                    
                                    groups_P.pop(longL[0])
                                    groups_P.append(new_outRing)
                                    groups_P.append(new_inRing)
                                    
                                else:                        
                                    ptProj=GetProjectivePoint(Point(endL[0],endL[1]), shortL[2])
                                    outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                                    
                                    new_pt0=point_on_line(Point(endS[0],endS[1]), shortP, (d1+d2)/2)
                                    new_pt1=point_on_line(Point(startL[0],startL[1]), longP, (d1+d2)/2) 
            
                                    new_outRing=outRing+[(ptProj.x, ptProj.y)]
                                    new_inRing=[(new_pt0.x,new_pt0.y)]+inRing+[(new_pt1.x,new_pt1.y)]
                                    
                                    groups_P.pop(longL[0])
                                    groups_P.append(new_outRing)
                                    groups_P.append(new_inRing)
                                               
                        elif longP.distance(Point(startL[0],startL[0]))<=60:
                            # situation 2
                            if verbose==True:
                                print 'Z shape(closed)'
    
                            ptProj0=GetProjectivePoint(Point(startS[0],startS[1]), longL[2])                         
                            ptProj1=GetProjectivePoint(Point(startL[0],startL[1]), shortL[2])
                            outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                             
                            new_outRing=outRing+[(ptProj0.x, ptProj0.y)]
                            new_inRing=[(ptProj1.x, ptProj1.y)]+inRing
                            
                            groups_P.pop(longL[0])
                            groups_P.append(new_outRing)
                            groups_P.append(new_inRing)
                            
                        else:
                            # situation 3
                            if verbose==True:
                                print '4 shape(closed)'
                                
                            ptProj=GetProjectivePoint(Point(startS[0],startS[1]), longL[2])
                            outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                            d1=shortP.distance(Point(startS[0],startS[1]))     
                            new_pt0=point_on_line(Point(endS[0],endS[1]), shortP, d1)
                            new_pt1=point_on_line(Point(startL[0],startL[1]), longP, d1) 
    
                            if groups_P[shortL[0]][shortL[1]] in outRing:
                                new_outRing=outRing+[(ptProj.x, ptProj.y)]
                                new_inRing=inRing+[(new_pt1.x,new_pt1.y)]+[(new_pt0.x,new_pt0.y)]
                            else:
                                new_outRing=outRing+[(new_pt1.x,new_pt1.y)]+[(new_pt0.x,new_pt0.y)]
                                new_inRing=inRing+[(ptProj.x, ptProj.y)]
                            
                            groups_P.pop(longL[0])
                            groups_P.append(new_outRing)
                            groups_P.append(new_inRing)    
                            
                    elif shortP.distance(Point(endS[0],endS[1]))<=60:
                        if longP.distance(Point(startL[0],startL[0]))<=60:
                            # situation 4
    
                            d1=shortP.distance(Point(endS[0],endS[0]))
                            d2=longP.distance(Point(startL[0],startL[1]))
                            
                            if math.fabs(d1-d2)/d1<=0.15:
                                if verbose==True:                            
                                    print 'U shape(closed)'
                                
                                outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
    
                                new_pt0=point_on_line(Point(startS[0],startS[1]), shortP, (d1+d2)/2)
                                new_pt1=point_on_line(Point(endL[0],endL[1]), longP, (d1+d2)/2)                        
                                
                                new_outRing=outRing
                                new_inRing=[(new_pt1.x,new_pt1.y)]+inRing+[(new_pt0.x,new_pt0.y)]
                                
                                groups_P.pop(longL[0])  
                                groups_P.append(new_outRing)
                                groups_P.append(new_inRing)
                                
                            else:
                                
                                if verbose==True:
                                    print 'U(Z) shape(closed)'
                                    
                                if d1<d2:
                                    ptProj=GetProjectivePoint(Point(endS[0],endS[1]), longL[2])
                                    outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                                    
                                    new_pt0=point_on_line(Point(startS[0],startS[1]), shortP, (d1+d2)/2)
                                    new_pt1=point_on_line(Point(endL[0],endL[1]), longP, (d1+d2)/2) 
            
                                    new_outRing=outRing+[(ptProj.x, ptProj.y)]
                                    new_inRing=[(new_pt1.x,new_pt1.y)]+inRing+[(new_pt0.x,new_pt0.y)]
                                    
                                    groups_P.pop(longL[0])
                                    groups_P.append(new_outRing)
                                    groups_P.append(new_inRing)
                                    
                                else:
                                    ptProj=GetProjectivePoint(Point(startL[0],startL[1]), shortL[2])
                                    outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                                    
                                    new_pt0=point_on_line(Point(startS[0],startS[1]), shortP, (d1+d2)/2)
                                    new_pt1=point_on_line(Point(endL[0],endL[1]), longP, (d1+d2)/2) 
            
                                    new_outRing=outRing+[(ptProj.x, ptProj.y)]
                                    new_inRing=[(new_pt1.x,new_pt1.y)]+inRing+[(new_pt0.x,new_pt0.y)]
                                    
                                    groups_P.pop(longL[0])
                                    groups_P.append(new_outRing)
                                    groups_P.append(new_inRing)
                            
                        elif longP.distance(Point(endL[0],endL[0]))<=60:
                            # situation 5
                            if verbose==True:                        
                                print 'Z shape(closed)'
                          
                            ptProj0=GetProjectivePoint(Point(endL[0],endL[1]), shortL[2])
                            ptProj1=GetProjectivePoint(Point(endS[0],endS[1]), longL[2])
                                    
                            outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                             
                            new_outRing=outRing+[(ptProj1.x, ptProj1.y)]
                            new_inRing=inRing+[(ptProj0.x, ptProj0.y)]
                            
                            groups_P.pop(longL[0])
                            groups_P.append(new_outRing)
                            groups_P.append(new_inRing)
                          
                        else:    
                            # situation 6
                            if verbose==True:
                                print '4 shape(closed)'
     
                            ptProj=GetProjectivePoint(Point(endS[0],endS[1]), longL[2])
                            outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                            d1=shortP.distance(Point(endS[0],endS[1]))  
                            new_pt0=point_on_line(Point(startS[0],startS[1]), shortP, d1)                   
                            new_pt1=point_on_line(Point(endL[0],endL[1]), longP, d1) 
    
                            if groups_P[shortL[0]][shortL[1]] in outRing:
                                new_outRing=outRing+[(new_pt0.x,new_pt0.y)]+[(new_pt1.x,new_pt1.y)]
                                new_inRing=inRing+[(ptProj.x, ptProj.y)]
                            else:
                                new_outRing=outRing+[(ptProj.x, ptProj.y)]
                                new_inRing=inRing+[(new_pt0.x,new_pt0.y)]+[(new_pt1.x,new_pt1.y)]
                            
                            groups_P.pop(longL[0])
                            groups_P.append(new_outRing)
                            groups_P.append(new_inRing) 
    
                    else:
                        if longP.distance(Point(startL[0],startL[0]))<=60:
                            # situation 7
                            if verbose==True:    
                                print '4 shape(closed)'
     
                            ptProj=GetProjectivePoint(Point(startL[0], startL[1]), shortL[2])
                            outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                            d1=longP.distance(Point(startL[0], startL[1]))  
                            new_pt0=point_on_line(Point(startS[0],startS[1]), shortP, d1)                   
                            new_pt1=point_on_line(Point(endL[0],endL[1]), longP, d1) 
    
                            new_outRing=outRing+[(ptProj.x, ptProj.y)]
                            new_inRing=[(new_pt1.x,new_pt1.y)]+inRing+[(new_pt0.x,new_pt0.y)]
                            
                            groups_P.pop(longL[0])
                            groups_P.append(new_outRing)
                            groups_P.append(new_inRing)        
                            
                        elif longP.distance(Point(endL[0],endL[0]))<=60:
                            # situation 8
                            if verbose==True:
                                print '4 shape(closed)'
     
                            ptProj=GetProjectivePoint(Point(endL[0], endL[1]), shortL[2])
                            outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                            d1=longP.distance(Point(endL[0],endL[1]))  
                            new_pt0=point_on_line(Point(endS[0],endS[1]), shortP, d1)                   
                            new_pt1=point_on_line(Point(startL[0],startL[1]), longP, d1) 
    
                            new_outRing=outRing+[(ptProj.x, ptProj.y)]
                            new_inRing=[(new_pt0.x,new_pt0.y)]+inRing+[(new_pt1.x,new_pt1.y)]
                            
                            groups_P.pop(longL[0])
                            groups_P.append(new_outRing)
                            groups_P.append(new_inRing) 
                            
                        else:
                            # situation 9
                            if verbose==True:                        
                                print 'H shape(closed)'
                            
                            new_pt0=point_on_line(Point(startS[0],startS[1]), shortP, width/2)
                            new_pt1=point_on_line(Point(endL[0],endL[1]), longP, width/2)
                            new_pt2=point_on_line(Point(startL[0],startL[1]), longP, width/2)
                            new_pt3=point_on_line(Point(endS[0],endS[1]), shortP, width/2)
        
                            outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                            
                            if groups_P[shortL[0]][shortL[1]] in outRing:                    
                                new_outRing=outRing+[(new_pt0.x,new_pt0.y)]+[(new_pt1.x,new_pt1.y)]
                                new_inRing=inRing+[(new_pt2.x,new_pt2.y)]+[(new_pt3.x,new_pt3.y)]
                            else:
                                new_outRing=outRing+[(new_pt2.x,new_pt2.y)]+[(new_pt3.x,new_pt3.y)]   
                                new_inRing=inRing+[(new_pt0.x,new_pt0.y)]+[(new_pt1.x,new_pt1.y)]         
                            
                            groups_P.pop(longL[0])
                            groups_P.append(new_outRing)
                            groups_P.append(new_inRing) 
    #------------------------------------------------------------------------------
    
    
    
    
    
    
                
                else:
                    outRing,inRing=separate_in_out(longL[1],shortL[1],groups_P[longL[0]])
                     
                    ptProj0=GetProjectivePoint(Point(groups_P[shortL[0]][shortL[1]][0], groups_P[shortL[0]][shortL[1]][1]), longL[2])
                    ptProj1=GetProjectivePoint(Point(groups_P[shortL[0]][shortL[1]+1][0], groups_P[shortL[0]][shortL[1]+1][1]), longL[2])
                    
                    if groups_P[shortL[0]][shortL[1]] in outRing:                    
                        new_outRing=outRing+[(ptProj0.x, ptProj0.y)]
                        new_inRing=[(ptProj1.x, ptProj1.y)]+inRing
                    else:
                        new_outRing=[(ptProj1.x, ptProj1.y)]+outRing
                        new_inRing=inRing+[(ptProj0.x, ptProj0.y)]                    
    
                        
                     
                    groups_P.pop(longL[0])  
                    groups_P.append(new_outRing)
                    groups_P.append(new_inRing)
    
            else:
                
    #------------------------------------------------------------------------------            
                if longL[2].length<=AVG_WALL_THICKNESS:
                    
                    if verbose==True:
                        print 'not self-closed','situation 1'
    
                    if math.fabs(longL[2].length-shortL[2].length)/shortL[2].length<=0.15:
                  
    #------------------------------------------------------------------------------                    
                        longGroup=groups_P[longL[0]]
                        reL=longGroup[longL[1]+1:]+longGroup[0:longL[1]+1]
    
                        shortGroup=groups_P[shortL[0]]
                        reS=shortGroup[shortL[1]+1:]+shortGroup[0:shortL[1]+1]
    
                        
                        if longL[0]>shortL[0]:
                            groups_P.pop(longL[0])                    
                            groups_P.pop(shortL[0])
                        else:
                            groups_P.pop(shortL[0]) 
                            groups_P.pop(longL[0])                    
                               
                        groups_P.append(reL+reS)
    #------------------------------------------------------------------------------  
                        
                    else:
                        print 'hahaha'
    #------------------------------------------------------------------------------                    
                        longGroup=groups_P[longL[0]]
                        reL=longGroup[longL[1]+1:]+longGroup[0:longL[1]+1]
    
                        shortGroup=groups_P[shortL[0]]
                        reS=shortGroup[shortL[1]+1:]+shortGroup[0:shortL[1]+1]
    
                        ptProj0=GetProjectivePoint(Point(shortGroup[shortL[1]][0],shortGroup[shortL[1]][1]), longL[2])
                        ptProj1=GetProjectivePoint(Point(shortGroup[shortL[1]+1][0],shortGroup[shortL[1]+1][1]), longL[2])
                        
                        if longL[0]>shortL[0]:
                            groups_P.pop(longL[0])                    
                            groups_P.pop(shortL[0])
                        else:
                            groups_P.pop(shortL[0]) 
                            groups_P.pop(longL[0])  
    
                        groups_P.append(reS+[(ptProj0.x, ptProj0.y)]+reL+[(ptProj1.x, ptProj1.y)])
    #------------------------------------------------------------------------------  
                        
                elif shortL[2].length>AVG_WALL_THICKNESS:
                    
                    if verbose==True:
                        print 'not self-closed','situation 2'
    
                    longGroup=groups_P[longL[0]]
                    reL=longGroup[longL[1]+1:]+longGroup[0:longL[1]+1]
    
                    shortGroup=groups_P[shortL[0]]
                    reS=shortGroup[shortL[1]+1:]+shortGroup[0:shortL[1]+1] 
                    
                    shortP=l1.intersection(shortL[2])
                    longP=l1.intersection(longL[2])
                    
                    startS=reS[-1]
                    endS=reS[0]
                    startL=reL[-1]
                    endL=reL[0]
                    
                    
                    if shortP.distance(Point(startS[0],startS[1]))<=60:
                        if longP.distance(Point(endL[0],endL[0]))<=60:
                            d1=shortP.distance(Point(startS[0],startS[1]))
                            d2=longP.distance(Point(endL[0],endL[0]))
                            
                            if math.fabs(d1-d2)/d1<=0.15:
                                if verbose==True:                            
                                    print 'U shape'
                                    
                                # situation 1
                                new_group=reS[0:]+reL[0:]
                                
                                new_pt=point_on_line(Point(startL[0],startL[1]), longP, (d1+d2)/2)                        
                                new_group.append((new_pt.x,new_pt.y))
                                new_pt=point_on_line(Point(endS[0],endS[1]), shortP, (d1+d2)/2)
                                new_group.append((new_pt.x,new_pt.y))
                                
                                if longL[0]>shortL[0]:
                                    groups_P.pop(longL[0])                    
                                    groups_P.pop(shortL[0])
                                else:
                                    groups_P.pop(shortL[0]) 
                                    groups_P.pop(longL[0])  
                                
                                groups_P.append(new_group)
                                
                            else:
                                if verbose==True:
                                    print 'U(Z) shape'
                                    
                                if d1<d2:
                                    ptProj=GetProjectivePoint(Point(startS[0],startS[1]), longL[2])
                                    new_group=reS[0:]+[(ptProj.x, ptProj.y)]+reL[0:]
                                    
                                    new_pt=point_on_line(Point(startL[0],startL[1]), longP, (d1+d2)/2)                        
                                    new_group.append((new_pt.x,new_pt.y))
                                    new_pt=point_on_line(Point(endS[0],endS[1]), shortP, (d1+d2)/2)
                                    new_group.append((new_pt.x,new_pt.y))
                                    
                                    if longL[0]>shortL[0]:
                                        groups_P.pop(longL[0])                    
                                        groups_P.pop(shortL[0])
                                    else:
                                        groups_P.pop(shortL[0]) 
                                        groups_P.pop(longL[0])  
                                    
                                    groups_P.append(new_group)
                                else:
                                    ptProj=GetProjectivePoint(Point(endL[0],endL[1]), shortL[2])
                                    new_group=reS[0:]+[(ptProj.x, ptProj.y)]+reL[0:]
                                    
                                    new_pt=point_on_line(Point(startL[0],startL[1]), longP, (d1+d2)/2)                        
                                    new_group.append((new_pt.x,new_pt.y))
                                    new_pt=point_on_line(Point(endS[0],endS[1]), shortP, (d1+d2)/2)
                                    new_group.append((new_pt.x,new_pt.y))
                                    
                                    if longL[0]>shortL[0]:
                                        groups_P.pop(longL[0])                    
                                        groups_P.pop(shortL[0])
                                    else:
                                        groups_P.pop(shortL[0]) 
                                        groups_P.pop(longL[0])  
                                    
                                    groups_P.append(new_group)
                            
                        elif longP.distance(Point(startL[0],startL[0]))<=60:
                            # situation 2
                            if verbose==True:
                                print 'Z shape'
                                
                            ptProj0=GetProjectivePoint(Point(startS[0],startS[1]), longL[2])
                            new_group=reS[0:]+[(ptProj0.x, ptProj0.y)]+reL[0:]
                             
                            ptProj1=GetProjectivePoint(Point(startL[0],startL[1]), shortL[2])
                            new_group.append((ptProj1.x, ptProj1.y))
                             
                            if longL[0]>shortL[0]:
                                groups_P.pop(longL[0])                    
                                groups_P.pop(shortL[0])
                            else:
                                groups_P.pop(shortL[0]) 
                                groups_P.pop(longL[0])  
                                
                            groups_P.append(new_group)
                            
                        else:
                            # situation 3
                            if verbose==True:
                                print '4 shape 1'
                                
                            ptProj0=GetProjectivePoint(Point(startS[0],startS[1]), longL[2])
                            new_group=reS[0:]+[(ptProj0.x, ptProj0.y)]+reL[0:]
                            
                            d1=shortP.distance(Point(startS[0],startS[1]))
                            new_pt=point_on_line(Point(startL[0],startL[1]), longP, d1)                        
                            new_group.append((new_pt.x,new_pt.y))
                            new_pt=point_on_line(Point(endS[0],endS[1]), shortP, d1)
                            new_group.append((new_pt.x,new_pt.y))
                            
                            if longL[0]>shortL[0]:
                                groups_P.pop(longL[0])                    
                                groups_P.pop(shortL[0])
                            else:
                                groups_P.pop(shortL[0]) 
                                groups_P.pop(longL[0])  
                                
                            groups_P.append(new_group)
                            
                    elif shortP.distance(Point(endS[0],endS[1]))<=60:
                        if longP.distance(Point(startL[0],startL[0]))<=60:
                            # situation 4
                            
                           
                            d1=shortP.distance(Point(endS[0],endS[0]))
                            d2=longP.distance(Point(startL[0],startL[1]))
                            
                            if math.fabs(d1-d2)/d1<=0.15:
                                if verbose==True:
                                    print 'U shape'
                                    
                                # situation 1
                                new_group=reL[0:]+reS[0:]
                                
    
                                new_pt=point_on_line(Point(startS[0],startS[1]), shortP, (d1+d2)/2)
                                new_group.append((new_pt.x,new_pt.y))                    
                                new_pt=point_on_line(Point(endL[0],endL[1]), longP, (d1+d2)/2)                        
                                new_group.append((new_pt.x,new_pt.y))
                                
                                if longL[0]>shortL[0]:
                                    groups_P.pop(longL[0])                    
                                    groups_P.pop(shortL[0])
                                else:
                                    groups_P.pop(shortL[0]) 
                                    groups_P.pop(longL[0])  
                                
                                groups_P.append(new_group)
                                
                            else:
                                if verbose==True:
                                    print 'U(Z) shape'
                                    
                                if d1<d2:
                                    ptProj=GetProjectivePoint(Point(endS[0],endS[1]), longL[2])
                                    new_group=reL[0:]+[(ptProj.x, ptProj.y)]+reS[0:]
                                    
                                    new_pt=point_on_line(Point(startS[0],startS[1]), shortP, (d1+d2)/2)
                                    new_group.append((new_pt.x,new_pt.y))                    
                                    new_pt=point_on_line(Point(endL[0],endL[1]), longP, (d1+d2)/2)                        
                                    new_group.append((new_pt.x,new_pt.y))
                                    
                                    if longL[0]>shortL[0]:
                                        groups_P.pop(longL[0])                    
                                        groups_P.pop(shortL[0])
                                    else:
                                        groups_P.pop(shortL[0]) 
                                        groups_P.pop(longL[0])  
                                    
                                    groups_P.append(new_group)
                                    
                                else:
                                    ptProj=GetProjectivePoint(Point(startL[0],startL[1]), shortL[2])
                                    new_group=reL[0:]+[(ptProj.x, ptProj.y)]+reS[0:]
                                    
                                    new_pt=point_on_line(Point(startS[0],startS[1]), shortP, (d1+d2)/2)
                                    new_group.append((new_pt.x,new_pt.y))                    
                                    new_pt=point_on_line(Point(endL[0],endL[1]), longP, (d1+d2)/2)                        
                                    new_group.append((new_pt.x,new_pt.y))
                                    
                                    if longL[0]>shortL[0]:
                                        groups_P.pop(longL[0])                    
                                        groups_P.pop(shortL[0])
                                    else:
                                        groups_P.pop(shortL[0]) 
                                        groups_P.pop(longL[0])  
                                    
                                    groups_P.append(new_group)
                            
                        elif longP.distance(Point(endL[0],endL[0]))<=60:
                            # situation 5
                            if verbose==True:
                                print 'Z shape'
                          
                            ptProj0=GetProjectivePoint(Point(endL[0],endL[1]), shortL[2])
                            new_group=reS[0:]+[(ptProj0.x, ptProj0.y)]+reL[0:]
                             
                            ptProj1=GetProjectivePoint(Point(endS[0],endS[1]), longL[2])
                            new_group.append((ptProj1.x, ptProj1.y))
                             
                            if longL[0]>shortL[0]:
                                groups_P.pop(longL[0])                    
                                groups_P.pop(shortL[0])
                            else:
                                groups_P.pop(shortL[0]) 
                                groups_P.pop(longL[0])  
                                
                            groups_P.append(new_group)
                            
                        else:
                            # situation 6
                            if verbose==True:
                                print '4 shape 2'
                                
                            d1=shortP.distance(Point(endS[0],endS[1]))
                            new_pt=point_on_line(Point(startS[0],startS[1]), shortP, d1)
                            new_group=reS[0:]+[(new_pt.x,new_pt.y)]
                        
                        
                            new_pt=point_on_line(Point(endL[0],endL[1]), longP, d1)
                            new_group.append((new_pt.x,new_pt.y))
                            new_group.extend(reL)
                        
                            ptProj=GetProjectivePoint(Point(endS[0],endS[1]), longL[2])
                            new_group.append((ptProj.x, ptProj.y))
                             
    
                            if longL[0]>shortL[0]:
                                groups_P.pop(longL[0])                    
                                groups_P.pop(shortL[0])
                            else:
                                groups_P.pop(shortL[0]) 
                                groups_P.pop(longL[0])  
                                
                            groups_P.append(new_group)
                    else:
                        if longP.distance(Point(startL[0],startL[0]))<=60:
                            # situation 7
                            if verbose==True:
                                print '4 shape 3'
                            
                            d1=longP.distance(Point(startL[0],startL[1]))   
                            new_pt0=point_on_line(Point(startS[0],startS[1]), shortP, d1)
                            new_pt1=point_on_line(Point(endL[0],endL[1]), longP, d1)
                            new_group=reS[0:]+[(new_pt0.x,new_pt0.y),(new_pt1.x,new_pt1.y)]+reL[0:]
    
                        
                            ptProj=GetProjectivePoint(Point(startL[0],startL[1]), shortL[2])
                            new_group.append((ptProj.x, ptProj.y))
                             
    
                            if longL[0]>shortL[0]:
                                groups_P.pop(longL[0])                    
                                groups_P.pop(shortL[0])
                            else:
                                groups_P.pop(shortL[0]) 
                                groups_P.pop(longL[0])  
                                
                            groups_P.append(new_group)
                            
                        elif longP.distance(Point(endL[0],endL[0]))<=60:
                            # situation 8
                            if verbose==True:
                                print '4 shape 4'
                            
                            d1=longP.distance(Point(endL[0],endL[1]))   
                            ptProj=GetProjectivePoint(Point(endL[0],endL[1]), shortL[2])
                            new_group=reS[0:]+[(ptProj.x, ptProj.y)]+reL[0:]
    
                            new_pt0=point_on_line(Point(startL[0],startL[1]), longP, d1)
                            new_pt1=point_on_line(Point(endS[0],endS[1]), shortP, d1)
                            
                            new_group.append((new_pt0.x,new_pt0.y))
                            new_group.append((new_pt1.x,new_pt1.y))
    
                            if longL[0]>shortL[0]:
                                groups_P.pop(longL[0])                    
                                groups_P.pop(shortL[0])
                            else:
                                groups_P.pop(shortL[0]) 
                                groups_P.pop(longL[0])  
                                
                            groups_P.append(new_group)
                            
                        else:
                            # situation 9
                            if verbose==True:
                                'H shape'
                                
                            new_pt=point_on_line(Point(startS[0],startS[1]), shortP, width/2)
                            new_group=reS[0:]+[(new_pt.x,new_pt.y)]
                            new_pt=point_on_line(Point(endL[0],endL[1]), longP, width/2)
                            new_group.append((new_pt.x,new_pt.y))
                            new_group.extend(reL)
                            new_pt=point_on_line(Point(startL[0],startL[1]), longP, width/2)
                            new_group.append((new_pt.x,new_pt.y))
                            new_pt=point_on_line(Point(endS[0],endS[1]), shortP, width/2)
                            new_group.append((new_pt.x,new_pt.y))
                            
                            if longL[0]>shortL[0]:
                                groups_P.pop(longL[0])                    
                                groups_P.pop(shortL[0])
                            else:
                                groups_P.pop(shortL[0]) 
                                groups_P.pop(longL[0])  
                                
                            groups_P.append(new_group)
                    
                else:
                    if verbose==True:
                        print 'not self-closed','situation 3'
    
    #------------------------------------------------------------------------------                    
                    longGroup=groups_P[longL[0]]
                    reL=longGroup[longL[1]+1:]+longGroup[0:longL[1]+1]
    
                    shortGroup=groups_P[shortL[0]]
                    reS=shortGroup[shortL[1]+1:]+shortGroup[0:shortL[1]+1]
                    
                    ptProj0=GetProjectivePoint(Point(shortGroup[shortL[1]][0], shortGroup[shortL[1]][1]), longL[2])
                    if shortL[1]+1>=len(shortGroup):
                        ptProj1=GetProjectivePoint(Point(shortGroup[shortL[1]+1-len(shortGroup)][0], shortGroup[shortL[1]+1-len(shortGroup)][1]), longL[2])
                    else:
                        ptProj1=GetProjectivePoint(Point(shortGroup[shortL[1]+1][0], shortGroup[shortL[1]+1][1]), longL[2])
                    
                    if longL[0]>shortL[0]:
                        groups_P.pop(longL[0])                    
                        groups_P.pop(shortL[0])
                    else:
                        groups_P.pop(shortL[0]) 
                        groups_P.pop(longL[0])  
    
                    groups_P.append(reS+[(ptProj0.x, ptProj0.y)]+reL+[(ptProj1.x, ptProj1.y)])
    #------------------------------------------------------------------------------                 
    
    new_groups_P0=[]
     
    for i in range(0, len(groups_P)):
        new_group=[]
        for j in range(0, len(groups_P[i])):
            if j==0:
                dv1_x = groups_P[i][-1][0] - groups_P[i][j][0]
                dv1_y = groups_P[i][-1][1] - groups_P[i][j][1]
                dv2_x = groups_P[i][j+1][0] - groups_P[i][j][0]
                dv2_y = groups_P[i][j+1][1] - groups_P[i][j][1]
            elif j==len(groups_P[i])-1:
                dv1_x = groups_P[i][j-1][0] - groups_P[i][j][0]
                dv1_y = groups_P[i][j-1][1] - groups_P[i][j][1]
                dv2_x = groups_P[i][0][0] - groups_P[i][j][0]
                dv2_y = groups_P[i][0][1] - groups_P[i][j][1]
            else:     
                dv1_x = groups_P[i][j-1][0] - groups_P[i][j][0]
                dv1_y = groups_P[i][j-1][1] - groups_P[i][j][1]
                dv2_x = groups_P[i][j+1][0] - groups_P[i][j][0]
                dv2_y = groups_P[i][j+1][1] - groups_P[i][j][1]
                
            dv1xdv2 = dv1_x * dv2_x + dv1_y * dv2_y
            absdv1 = math.sqrt(dv1_x * dv1_x + dv1_y * dv1_y)
            absdv2 = math.sqrt(dv2_x * dv2_x + dv2_y * dv2_y)
            if absdv1==0:
                if j<=1:
                    dv1_x = groups_P[i][j-2+len(groups_P[i])][0] - groups_P[i][j][0]
                    dv1_y = groups_P[i][j-2+len(groups_P[i])][1] - groups_P[i][j][1]
                else:
                    dv1_x = groups_P[i][j-2][0] - groups_P[i][j][0]
                    dv1_y = groups_P[i][j-2][1] - groups_P[i][j][1]
                
                dv1xdv2 = dv1_x * dv2_x + dv1_y * dv2_y
                absdv1 = math.sqrt(dv1_x * dv1_x + dv1_y * dv1_y)
                absdv2 = math.sqrt(dv2_x * dv2_x + dv2_y * dv2_y)
                angle = math.degrees(math.acos(dv1xdv2 / (absdv1 * absdv2)))
                
                if math.fabs(angle)>=3 and math.fabs(angle)<=177:
                    new_group.append((groups_P[i][j][0], groups_P[i][j][1]))
                    
            elif absdv2==0:
                continue
            else:
                if dv1xdv2 / (absdv1 * absdv2)>1:
                    angle=math.degrees(math.acos(1))
                elif dv1xdv2 / (absdv1 * absdv2)<-1:
                    angle=math.degrees(math.acos(-1))
                else:
                    angle = math.degrees(math.acos(dv1xdv2 / (absdv1 * absdv2)))
                if math.fabs(angle)>=3 and math.fabs(angle)<=177:
                    new_group.append((groups_P[i][j][0], groups_P[i][j][1]))
                
        new_groups_P0.append(new_group)
#------------------------------------------------------------------------------
        new_groups_P=[]
        for i in range(0, len(new_groups_P0)):
            if len(new_groups_P0[i])>2:
                new_groups_P.append(list(Polygon(new_groups_P0[i]).buffer(0).exterior.coords))
#------------------------------------------------------------------------------
      
    return new_groups_P, Nodes
