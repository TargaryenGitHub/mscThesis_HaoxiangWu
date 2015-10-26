from shapely.geometry import Point
from shapely.geometry import LineString 
from shapely.geometry import Polygon
import dxfgrabber
import fiona
import math
from collections import OrderedDict



def separate_in_out(i1,i2,arrayP):
        
    if i1>i2:
        b=i1
        s=i2
    else:
        b=i2
        s=i1
        
    if b+1<len(arrayP):
        a1=arrayP[s+1:b+1]
        a2=arrayP[b+1:]+arrayP[0:s+1]
    else:  
        a1=arrayP[(b+1-len(arrayP)):s+1]
        a2=arrayP[s+1:]+arrayP[0:b+1-len(arrayP)]
    
    s1=0
    for i in range(0, len(a1)):
        if i==len(a1)-1:
            s1=s1+a1[i][0]*a1[0][1]-a1[i][1]*a1[0][0]
        else:
            s1=s1+a1[i][0]*a1[i+1][1]-a1[i][1]*a1[i+1][0]
    
    s2=0
    for i in range(0, len(a2)):
        if i==len(a2)-1:
            s2=s2+a2[i][0]*a2[0][1]-a2[i][1]*a2[0][0]
        else:
            s2=s2+a2[i][0]*a2[i+1][1]-a2[i][1]*a2[i+1][0]
            
    if math.fabs(s1)>math.fabs(s2):
        return [a1,a2]
    else:
        return [a2,a1]


def dist_p2l(p0, p1, p2):
    A=p2.y-p1.y
    B=p1.x-p2.x
    C=p2.x*p1.y-p2.y*p1.x
    d=math.fabs(p0.x*A+p0.y*B+C)/math.sqrt(A*A+B*B)
    return d


def GetProjectivePoint(p0, l1):
    x0=p0.x
    y0=p0.y
    x1=list(l1.coords)[0][0]
    y1=list(l1.coords)[0][1]
    x2=list(l1.coords)[1][0]
    y2=list(l1.coords)[1][1]
    
    if math.fabs(x1-x2)<=0.01:
        ProjX=(x1+x2)/2
        ProjY=y0
    elif math.fabs(y1-y2)<=0.01:
        ProjX=x0
        ProjY=(y1+y2)/2
    else:
        k=(y2-y1)/(x2-x1)
        ProjX=(k*k*x1+x0+k*(y0-y1))/(k*k+1)
        ProjY=(-1/k)*(ProjX-x0)+y0
    
    return Point(ProjX, ProjY)
        
        
        
        
        
def coordtransformation(p0, angle, X0, Y0, xs, ys):

    X=xs*p0.x*math.cos(angle)-ys*p0.y*math.sin(angle)+X0
    Y=xs*p0.x*math.sin(angle)+ys*p0.y*math.cos(angle)+Y0

#    X=xs*(p0.x*math.cos(angle)-p0.y*math.sin(angle))+X0
#    Y=ys*(p0.x*math.sin(angle)+p0.y*math.cos(angle))+Y0
    
    return Point(X,Y)


def blockbbox(block, dxf, X0, Y0, angle, xs, ys):
    anchors=[]
    lines=[]
    
    xmin=float('inf')
    xmax=float('-inf')
    ymin=float('inf')
    ymax=float('-inf')        
    
    for j in dxf.blocks[block.name]:

#------------------------------------------------------------------------------        
        if j.dxftype=='LINE':
            
            if j.start[0]>xmax:
                xmax=j.start[0]
            
            if j.start[0]<xmin:
                xmin=j.start[0]
            
            if j.start[1]>ymax:
                ymax=j.start[1]
            
            if j.start[1]<ymin:
                ymin=j.start[1]
            
            if j.end[0]>xmax:
                xmax=j.end[0]
            
            if j.end[0]<xmin:
                xmin=j.end[0]
            
            if j.end[1]>ymax:
                ymax=j.end[1]
            
            if j.end[1]<ymin:
                ymin=j.end[1]
            
            lines.append(LineString([(j.start[0], j.start[1]), (j.end[0], j.end[1])]))
            
#------------------------------------------------------------------------------   
            
        elif j.dxftype=='POLYLINE':
            
            if j.is_closed==True:
                lines.append(LineString([(j.points[0][0], j.points[0][1]), (j.points[-1][0], j.points[-1][1])]))
                
            for k in range(0, len(j.points)):

                if j.points[k][0]>xmax:
                    xmax=j.points[k][0]
                
                if j.points[k][0]<xmin:
                    xmin=j.points[k][0]
                
                if j.points[k][1]>ymax:
                    ymax=j.points[k][1]
                
                if j.points[k][1]<ymin:
                    ymin=j.points[k][1]
                   
                if k<len(j.points)-1:
                    lines.append(LineString([(j.points[k][0], j.points[k][1]), (j.points[k+1][0], j.points[k+1][1])]))

#------------------------------------------------------------------------------    
                    
        elif j.dxftype=='LWPOLYLINE':
            
            if j.is_closed==True:
                lines.append(LineString([(j.points[0][0], j.points[0][1]), (j.points[-1][0], j.points[-1][1])]))
                
            for k in range(0, len(j.points)):
                
                
                
                if j.points[k][0]>xmax:
                    xmax=j.points[k][0]
                
                if j.points[k][0]<xmin:
                    xmin=j.points[k][0]
                
                if j.points[k][1]>ymax:
                    ymax=j.points[k][1]
                
                if j.points[k][1]<ymin:
                    ymin=j.points[k][1]
                
                if k<len(j.points)-1:
                    lines.append(LineString([(j.points[k][0], j.points[k][1]), (j.points[k+1][0], j.points[k+1][1])]))

#------------------------------------------------------------------------------    
                        
        elif j.dxftype=='ARC':
            
            anchors.append(Point(j.center[0], j.center[1]))
         
            if j.center[0]>xmax:
                xmax=j.center[0]
            
            if j.center[0]<xmin:
                xmin=j.center[0]
            
            if j.center[1]>ymax:
                ymax=j.center[1]
            
            if j.center[1]<ymin:
                ymin=j.center[1]
        
                    
            x0=j.center[0]+j.radius*math.cos(math.radians(j.startangle))
            y0=j.center[1]+j.radius*math.sin(math.radians(j.startangle))
            x1=j.center[0]+j.radius*math.cos(math.radians(j.endangle))
            y1=j.center[1]+j.radius*math.sin(math.radians(j.endangle))
                 
            
            if x0>xmax:
                xmax=x0
            
            if x0<xmin:
                xmin=x0
            
            if y0>ymax:
                ymax=y0
            
            if y0<ymin:
                ymin=y0
                        
            if x1>xmax:
                xmax=x1
            
            if x1<xmin:
                xmin=x1
            
            if y1>ymax:
                ymax=y1
            
            if y1<ymin:
                ymin=y1


            lines.append(LineString([(j.center[0], j.center[1]), (x0, y0)]))    
            lines.append(LineString([(j.center[0], j.center[1]), (x1, y1)])) 
            lines.append(LineString([(x0, y0), (x1, y1)]))
 
#------------------------------------------------------------------------------   
                
        elif j.dxftype=='INSERT':
            
            X0_0=j.insert[0]
            Y0_0=j.insert[1]
            angle_0=math.radians(j.rotation)
            xs_0=j.scale[0]
            ys_0=j.scale[1]
            
            
            
            result=blockbbox(j, dxf, X0_0, Y0_0, angle_0, xs_0, ys_0)

            for i in range(0,4):
                
                if result[i].x<xmin:
                    xmin=result[i].x
                if result[i].x>xmax:
                    xmax=result[i].x
                if result[i].y<ymin:
                    ymin=result[i].y
                if result[i].y>ymax:
                    ymax=result[i].y
            
            lines.extend(result[4])
            anchors.extend(result[5])
                        
#------------------------------------------------------------------------------
    
    if len(anchors)>0:
        
        p1=Point(xmin,ymin)  
        p2=Point(xmax,ymin)
        p3=Point(xmax,ymax)
        p4=Point(xmin,ymax)
        
        
        if p1.distance(p2)>=p2.distance(p3):
            d1=dist_p2l(anchors[0], p1, p2)
            d2=dist_p2l(anchors[0], p3, p4)
            p14=Point((p1.x+p4.x)/2, (p1.y+p4.y)/2)
            p23=Point((p2.x+p3.x)/2, (p2.y+p3.y)/2)
            d3=dist_p2l(anchors[0], p14, p23)
            
            if d1<=d2 and d1<=d3:
                ymax=ymin+120
                
            elif d2<=d1 and d2<=d3:
                ymin=ymax-120
                
            else:
                ymax=p14.y+120/2
                ymin=p14.y-120/2
                    
        else:
            d1=dist_p2l(anchors[0], p1, p4)
            d2=dist_p2l(anchors[0], p2, p3)
            p12=Point((p1.x+p2.x)/2, (p1.y+p2.y)/2)
            p34=Point((p3.x+p4.x)/2, (p3.y+p4.y)/2)
            d3=dist_p2l(anchors[0], p12, p34)
            
            if d1<=d2 and d1<=d3:
                xmax=xmin+120
                
            elif d2<=d1 and d2<=d3:
                xmin=xmax-120
                
            else:
                xmax=p12.x+120/2
                xmin=p12.x-120/2
    
    
    
    
    new_lines=[]         
    for line in lines:
        p0=coordtransformation(Point(list(line.coords)[0]), angle, X0, Y0, xs, ys)
        p1=coordtransformation(Point(list(line.coords)[1]), angle, X0, Y0, xs, ys)
        new_lines.append(LineString([(p0.x, p0.y),(p1.x, p1.y)]))
    
    new_anchors=[]
    if len(anchors)>0:
        for anchor in anchors:
            new_anchor=coordtransformation(anchor, angle, X0, Y0, xs, ys)
            new_anchors.append(new_anchor)
         
                
                
    p1=coordtransformation(Point(xmin,ymin), angle, X0, Y0, xs, ys)     
    p2=coordtransformation(Point(xmax,ymin), angle, X0, Y0, xs, ys) 
    p3=coordtransformation(Point(xmax,ymax), angle, X0, Y0, xs, ys)  
    p4=coordtransformation(Point(xmin,ymax), angle, X0, Y0, xs, ys) 

    return [p1, p2, p3, p4, new_lines, new_anchors]








#------------------------------------------------------------------------------
if __name__ == "__main__":
    filename='aaaaa.dxf'
    #filename='BK_preprocessed.dxf'
    wall_layer='Walls'
    window_layer='Windows'
    door_layer='Doors'
    MINIMALDIST=5
    
    
    dxf = dxfgrabber.readfile(filename, {"grab_blocks":True, "assure_3d_coords":False, "resolve_text_styles":False})
    
    
    windows=[]
    doors=[]
    
    
    aaa=[]
    aaa.append(LineString([(0,0),(0,1000)]))
    aaa.append(LineString([(0,0),(1000,0)]))
    bbb=[]
    
    
    for i in dxf.entities:
        if i.dxftype=='INSERT':
            
            X0=i.insert[0]
            Y0=i.insert[1]
            angle=math.radians(i.rotation)
            xs=i.scale[0]
            ys=i.scale[1]        
            
            
            result=blockbbox(i, dxf, X0, Y0, angle, xs, ys)
            
            
    
            p1=result[0]
            p2=result[1]
            p3=result[2]
            p4=result[3]
            aaa.extend(result[4])
            bbb.extend(result[5])
    
            
            aaa.append(LineString([(p1.x, p1.y), (p2.x, p2.y)]))
            aaa.append(LineString([(p2.x, p2.y), (p3.x, p3.y)]))
            aaa.append(LineString([(p3.x, p3.y), (p4.x, p4.y)]))
            aaa.append(LineString([(p4.x, p4.y), (p1.x, p1.y)]))

                
    
            
            ply=Polygon([(p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y), (p4.x, p4.y)]) 
            
    
                
            
            
            
    
    
    
#------------------------------------------------------------------------------
    with fiona.open('only_walls.shp') as source:
        source_driver = source.driver
        source_crs = source.crs
        source_schema = source.schema    
    
    
        
        with fiona.open('linepairs.shp', 'w', crs=source_crs, driver=source_driver, schema=source_schema,) as c:
            k=0
            for i in range(0, len(aaa)):
                coordinates=list(aaa[i].coords)
                rec = {'geometry':{'coordinates':coordinates, 
                                   'type': 'LineString'},
                       'id': str(k),
                       'properties': OrderedDict([(u'myid', str(k))]),
                       'type': 'Feature'}               
                c.write(rec)
                k=k+1
        c.close()

                
    if len(bbb)>0:
        with fiona.open('pts.shp') as source:
            source_driver = source.driver
            source_crs = source.crs
            source_schema = source.schema    
        
        
            
            with fiona.open('new_pts.shp', 'w', crs=source_crs, driver=source_driver, schema=source_schema,) as c:
                k=0
                for i in range(0, len(bbb)):
                    coordinates=(bbb[i].x, bbb[i].y)
                    rec = {'geometry':{'coordinates':coordinates, 
                                       'type': 'Point'},
                           'id': str(k),
                           'properties': OrderedDict([(u'id', str(k))]),
                           'type': 'Feature'}               
                    c.write(rec)
                    k=k+1
            c.close()
        
        



