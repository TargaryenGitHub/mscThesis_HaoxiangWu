import math
import shapefile
import dxfgrabber

from shapely.geometry import Point
from shapely.geometry import LineString 

from untitled0 import blockbbox


from extend_line import extend_line_onedir
from extend_line import extend_line_bothdir

from Opening import Door
from Opening import Window

    
    
    
def calcOpeningBoundingBox(abs_file_path, WINDOW_LAYER_NAME, DOOR_LAYER_NAME):
    
    dxf = dxfgrabber.readfile(abs_file_path, {"grab_blocks":True, "assure_3d_coords":False, "resolve_text_styles":False})
    windows=[]
    doors=[]

    for i in dxf.entities:
        
# -------------------------------- Windows ------------------------------------     
        if i.layer == WINDOW_LAYER_NAME and i.dxftype == 'INSERT':
            
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
        
            if p1.distance(p2)>=p2.distance(p3):
                pp1,pp2=extend_line_bothdir(Point((p1.x+p4.x)/2, (p1.y+p4.y)/2), Point((p2.x+p3.x)/2, (p2.y+p3.y)/2), 20)
                width=p2.distance(p3)
                length=Point((p1.x+p4.x)/2, (p1.y+p4.y)/2).distance(Point((p2.x+p3.x)/2, (p2.y+p3.y)/2))
            else:
                pp1,pp2=extend_line_bothdir(Point((p1.x+p2.x)/2, (p1.y+p2.y)/2), Point((p3.x+p4.x)/2, (p3.y+p4.y)/2), 20)
                width=p1.distance(p2)
                length=Point((p1.x+p2.x)/2, (p1.y+p2.y)/2).distance(Point((p3.x+p4.x)/2, (p3.y+p4.y)/2))
                
            windows.append(Window(LineString([(pp1.x,pp1.y),(pp2.x,pp2.y)]), width, length))
            
            
# --------------------------------- Doors ------------------------------------- 
        if i.layer == DOOR_LAYER_NAME and i.dxftype == 'INSERT':
            
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
             
            if p1.distance(p2)>=p2.distance(p3):
                pp1,pp2=extend_line_bothdir(Point((p1.x+p4.x)/2, (p1.y+p4.y)/2), Point((p2.x+p3.x)/2, (p2.y+p3.y)/2), 20)
                width=p2.distance(p3)
                length=Point((p1.x+p4.x)/2, (p1.y+p4.y)/2).distance(Point((p2.x+p3.x)/2, (p2.y+p3.y)/2))
            else:
                pp1,pp2=extend_line_bothdir(Point((p1.x+p2.x)/2, (p1.y+p2.y)/2), Point((p3.x+p4.x)/2, (p3.y+p4.y)/2), 20)
                width=p1.distance(p2)
                length=Point((p1.x+p2.x)/2, (p1.y+p2.y)/2).distance(Point((p3.x+p4.x)/2, (p3.y+p4.y)/2))
                
            doors.append(Door(LineString([(pp1.x,pp1.y),(pp2.x,pp2.y)]), width, length))
#------------------------------------------------------------------------------            
             
    print '#-----------------------------'             
    print 'len(windows)', len(windows)  
    print 'len(doors)', len(doors) 
        
    openings=[]
    openings.extend(windows)
    openings.extend(doors)
    
    return openings
