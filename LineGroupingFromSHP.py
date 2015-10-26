import math
import shapefile

from shapely.geometry import Point
from shapely.geometry import LineString 
from shapely.geometry import Polygon
from shapely.geometry import polygon

from fix_drafting_errors import fix_disjoint_vertices


def LineGroupingFromSHP(abs_file_path, MINIMALDIST):
    

    sf = shapefile.Reader(abs_file_path)

#------------------------ read lines from shapefile ---------------------------
    chains=[]
    for geom in sf.shapeRecords():

        chain=[(geom.shape.points[0][0],geom.shape.points[0][1]),(geom.shape.points[1][0],geom.shape.points[1][1])]
        chains.append(chain)

#------------------------------------------------------------------------------
    
    
#------------------ group lines & fix unconnected vertices --------------------
    closed_chains=[]
    
    k=1
    RADIUS=MINIMALDIST
    
    print '#-----------------------------'
    print 'k=', k, 'RADIUS=', RADIUS
    print 'len(chains)', len(chains)           
    print 'len(closed_chains)', len(closed_chains)
    
    while (k<=5 and len(chains)>0):
        
    
        
        if len(chains)==1:
            pt11=Point(chains[0][0][0], chains[0][0][1])
            pt12=Point(chains[0][-1][0],chains[0][-1][1])
            
            if pt11.distance(pt12)<=RADIUS:
                chains.pop(0)
                l1=LineString([chain1[0], chain1[1]])
                l2=LineString([chain1[-1], chain1[-2]])
                new_pts1=fix_disjoint_vertices(l1, l2)
                new_chain=chain1[1:-1]+new_pts1
                closed_chains.append(new_chain)
                break
            else:
                print 'wawawa'
                k=k+1
                RADIUS=RADIUS+MINIMALDIST
                
                print '#-----------------------------'
                print 'k=', k, 'RADIUS=', RADIUS
                print 'len(chains)', len(chains)           
                print 'len(closed_chains)', len(closed_chains)
                
                break
        
        L=len(chains)
        for i in range(0, len(chains)-1):
            
            chain1=chains[i]
            pt11=Point(chain1[0][0], chain1[0][1])
            pt12=Point(chain1[-1][0],chain1[-1][1])
            
            if pt11.distance(pt12)<=RADIUS:
                chains.pop(i)
                l1=LineString([chain1[0], chain1[1]])
                l2=LineString([chain1[-1], chain1[-2]])
                new_pts1=fix_disjoint_vertices(l1, l2)
                new_chain=chain1[1:-1]+new_pts1
                closed_chains.append(new_chain)
                break
            
            
            for j in range(i+1, len(chains)+1):
                
                if j==len(chains):
                    break
                
                chain2=chains[j]
                pt21=Point(chain2[0][0], chain2[0][1])
                pt22=Point(chain2[-1][0],chain2[-1][1])
                
                if pt11.distance(pt21)<=RADIUS:
                    l1=LineString([chain1[0], chain1[1]])
                    l2=LineString([chain2[0], chain2[1]])
                    new_pts1=fix_disjoint_vertices(l1, l2)
                    
                    if pt12.distance(pt22)<=RADIUS:
                        # closed
                        l1=LineString([chain1[-1], chain1[-2]])
                        l2=LineString([chain2[-1], chain2[-2]])
                        new_pts2=fix_disjoint_vertices(l1, l2)
                        
                        chains.pop(j)
                        chains.pop(i)
                        chain1.reverse()
                        new_chain=new_pts2+chain1[1:-1]+new_pts1+chain2[1:-1]
                        closed_chains.append(new_chain)
                        break
                    
                    else:
                        chains.pop(j)
                        chains.pop(i)
                        chain1.reverse()
                        new_chain=chain1[0:-1]+new_pts1+chain2[1:]
                        chains.append(new_chain)
                        break
                    
                elif pt11.distance(pt22)<=RADIUS:
                    l1=LineString([chain1[0], chain1[1]])
                    l2=LineString([chain2[-1], chain2[-2]])
                    new_pts1=fix_disjoint_vertices(l1, l2)
                    
                    if pt12.distance(pt21)<=RADIUS:
                        # closed
                        l1=LineString([chain1[-1], chain1[-2]])
                        l2=LineString([chain2[0], chain2[1]])
                        new_pts2=fix_disjoint_vertices(l1, l2)
                        
                        chains.pop(j)
                        chains.pop(i)
                        new_chain=new_pts1+chain1[1:-1]+new_pts2+chain2[1:-1]
                        closed_chains.append(new_chain)
                        break
                    
                    else:
                        chains.pop(j)
                        chains.pop(i)
                        new_chain=chain2[0:-1]+new_pts1+chain1[1:]
                        chains.append(new_chain)
                        break
                    
                elif pt12.distance(pt21)<=RADIUS:
                    l1=LineString([chain1[-1], chain1[-2]])
                    l2=LineString([chain2[0], chain2[1]])
                    new_pts1=fix_disjoint_vertices(l1, l2)
            
                    chains.pop(j)
                    chains.pop(i)
                    new_chain=chain1[0:-1]+new_pts1+chain2[1:]
                    chains.append(new_chain)
                    break
                    
                elif pt12.distance(pt22)<=RADIUS:
                    l1=LineString([chain1[-1], chain1[-2]])
                    l2=LineString([chain2[-1], chain2[-2]])
                    new_pts1=fix_disjoint_vertices(l1, l2)
                
                    chains.pop(j)
                    chains.pop(i)
                    chain2.reverse()
                    new_chain=chain1[0:-1]+new_pts1+chain2[1:]
                    chains.append(new_chain)
                    break
                
                else:
                    continue
                
            if j==L:
                continue
            else:
                break
            
        if i==L-2 and j==L:
            print 'hahaha'
            k=k+1
            RADIUS=RADIUS+MINIMALDIST
            
            print '#-----------------------------'
            print 'k=', k, 'RADIUS=', RADIUS
            print 'len(chains)', len(chains)           
            print 'len(closed_chains)', len(closed_chains)
    
        else:
            continue
    
    
    
    
    print '#-----------------------------'
    print 'len(chains)', len(chains)           
    print 'len(closed_chains)', len(closed_chains)      


#------------------------------------------------------------------------------             
    

#------------------------------------------------------------------------------    
    groups_P=[]
    
    for i in range(0, len(closed_chains)):
        
        if len(closed_chains[i])>2:
            if Polygon(closed_chains[i]).is_valid==True:
                ply=Polygon(closed_chains[i])
                new_ply=polygon.orient(ply, sign=1.0)
                groups_P.append(list(new_ply.exterior.coords)[0:-1])
      
            else:
                ply=Polygon(closed_chains[i]).buffer(0).exterior.coords
                new_ply=polygon.orient(ply, sign=1.0)
                groups_P.append(list(new_ply.exterior.coords)[0:-1])
        else:
            print 'closed_chains ',i,' only has two points'

    
    return groups_P
#------------------------------------------------------------------------------
