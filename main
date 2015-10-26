import os  
import time
import math
import shapefile
import fiona
import psycopg2
import dxfgrabber

from shapely.geometry import Point
from shapely.geometry import LineString 
from shapely.geometry import Polygon
from shapely.geometry import polygon
    
  
    
from collections import OrderedDict
from fix_drafting_errors import fix_duplicated_lines
from fix_drafting_errors import fix_disjoint_vertices

from untitled0 import blockbbox
from untitled0 import dist_p2l
from untitled0 import GetProjectivePoint
from untitled0 import separate_in_out

from extend_line import extend_line_onedir
from extend_line import extend_line_bothdir

from Opening import Door
from Opening import Window
from LineGroupingFromSHP import LineGroupingFromSHP
from calcOpeningBoundingBox import calcOpeningBoundingBox
from ContourReconstruction00 import ContourReconstruction00
        
        
        
start_time = time.time()

#------------------------- INPUT & OUTPUT SETTINGS ----------------------------
#DXF_FILENAMES=['EB_alle_niveaus_ground_floor_changed.dxf', 'EB_alle_niveaus_first_floor_changed.dxf', 'EB_alle_niveaus_second_floor_changed.dxf', 'EB_alle_niveaus_second_floor_changed.dxf']
#DXF_FILENAMES=['BK_preprocessed_changed.dxf','BK_preprocessed_changed.dxf','BK_preprocessed_changed.dxf']
DXF_FILENAMES=['Binnenvest_03.dxf','Binnenvest_01_changed.dxf','Binnenvest_02_changed.dxf']
#DXF_FILENAMES=['Binnenvest_01_changed.dxf','Binnenvest_02_changed.dxf']


WALL_LAYER_NAME='Walls'
WINDOW_LAYER_NAME='Windows'
DOOR_LAYER_NAME='Doors'
sourceCRS_EPSG=31463

#SHP_FILENAMES=['EB_alle_niveaus_ground_floor_fixed.shp', 'EB_alle_niveaus_first_floor_fixed.shp', 'EB_alle_niveaus_second_floor_fixed.shp', 'EB_alle_niveaus_second_floor_fixed.shp']
#SHP_FILENAMES=['BK_preprocessed_fixed.shp','BK_preprocessed_fixed.shp','BK_preprocessed_fixed.shp']
SHP_FILENAMES=['Binnenvest_03_fixed.shp','Binnenvest_01_fixed.shp','Binnenvest_02_fixed.shp']
#SHP_FILENAMES=[Binnenvest_01_fixed.shp','Binnenvest_02_fixed.shp']




EXPORT_DATA_INTO_DATABASE=True

#EXPORT_DATA_INTO_QGIS=True
#------------------------------------------------------------------------------


#---------------------------- DATABASE SETTINGS -------------------------------
#DBNAME="EB_alle_niveaus"
DBNAME="Binnenvest"
USER="postgres"
PASSWORD="lyyz064101011"
#------------------------------------------------------------------------------


#---------------------- BUILDING GENERAL INFORMATION --------------------------
BUILDINGNAME='Binnenvest'
BUILDINGHEIGHT=12
BUILDINGLEVELS=3
MINLEVEL=0
MAXLEVEL=2

#FLOORNAMES=['GroundFloor','FirstFloor','SecondFloor','ThirdFloor']
FLOORNAMES=['Basement','GroundFloor','FirstFloor']
LEVELHEIGHT=4
ROOMHEIGHT=3
DOORHEIGHT=2.5
WINDOWHEIGHT=1.5
WINDOWBREAST=0.5
#------------------------------------------------------------------------------





#-------------------------- 2D PROCESSING SETTINGS ----------------------------
MINIMALDIST=5

#AVG_WALL_THICKNESS=230
#AVG_WALL_THICKNESS=800
AVG_WALL_THICKNESS=450

verbose=False  # provide detailed information while processing
#------------------------------------------------------------------------------




#-------------------------configure the database-------------------------------
if EXPORT_DATA_INTO_DATABASE==True:
    
    # Connect to an existing database
    conn = psycopg2.connect("dbname=" + DBNAME + " user=" + USER + " password=" + PASSWORD + "")
    
    # Open a cursor to perform database operations
    cur = conn.cursor()
    
    
    # Drop all tables if they exist.
    cur.execute(""" 
                    DROP TABLE IF EXISTS nodes;
                    DROP TABLE IF EXISTS ways;
                    DROP TABLE IF EXISTS way_nodes;
                    DROP TABLE IF EXISTS relations;
                    DROP TABLE IF EXISTS relation_members;
                """)
   
    # Create a table for nodes.
    cur.execute(""" CREATE TABLE nodes (id bigint NOT NULL,
                                        tags hstore);
                """)
     
     # Create a table for ways.
    cur.execute("""CREATE TABLE ways (id bigint NOT NULL,
                                      tags hstore);
                """)
                
    # Add a postgis point column holding the location of the node.
    cur.execute("SELECT AddGeometryColumn('nodes', 'geom', " + str(sourceCRS_EPSG) + ", 'POINT', 2);")
    cur.execute("SELECT AddGeometryColumn('ways', 'linestring', " + str(sourceCRS_EPSG) + ", 'LINESTRING', 2);")
    
    # Create a table for relations.
    cur.execute("""CREATE TABLE relations (id bigint NOT NULL,
                                           tags hstore);""")
    
    # Create a table for representing relation member relationships.
    cur.execute("""CREATE TABLE relation_members (relation_id bigint NOT NULL,
                                                  member_id bigint NOT NULL,
                                                  member_type character(1) NOT NULL,
                                                  member_role text NOT NULL);""")
     
    # Add primary keys to tables.
    cur.execute(""" ALTER TABLE ONLY nodes ADD CONSTRAINT pk_nodes PRIMARY KEY (id);             
                    ALTER TABLE ONLY ways ADD CONSTRAINT pk_ways PRIMARY KEY (id);                
                   
                    ALTER TABLE ONLY relations ADD CONSTRAINT pk_relations PRIMARY KEY (id);               
                    ALTER TABLE ONLY relation_members ADD CONSTRAINT pk_relation_members PRIMARY KEY (relation_id, member_id);
                """)
   
    # Add indexes to tables.
    cur.execute(""" CREATE INDEX idx_nodes_geom ON nodes USING gist (geom);
                    CREATE INDEX idx_relation_members_member_id_and_type ON relation_members USING btree (member_id, member_type);
                """)

    # Set to cluster nodes by geographical location.
    cur.execute("""ALTER TABLE ONLY nodes CLUSTER ON idx_nodes_geom;""")
    
    # Set to cluster the tables showing relationship by parent ID and sequence
    cur.execute("ALTER TABLE ONLY relation_members CLUSTER ON pk_relation_members;")
    
    # Insert the building relation record into TABLE RELATION
    tag="hstore(array['type','building','height','name','building:levels','building:max_level','building:min_level'],array['building', 'yes', '" + str(BUILDINGHEIGHT) +"', '" + BUILDINGNAME + "', '" + str(BUILDINGLEVELS)+ "','" + str(MAXLEVEL) + "','" + str(MINLEVEL)+"'])"
    cur.execute("INSERT INTO relations (id, tags) VALUES (" + str(0) + ", " + tag + ");")
                
    # Make the changes to the database persistent
    conn.commit()
#------------------------------------------------------------------------------





#----------------------------- for each floor ---------------------------------
numNODES=0
numWAYS=0
levelID=1

for level in range(MINLEVEL, MAXLEVEL+1):
    
    print "#-----------------------------"
    print "This is level: "+str(level)
    
    script_dir = os.path.dirname(__file__)
# ------------- Unconnected vertices fixing & lines grouping ------------------    
    # groupedPoints is groups of points representing wall polygons
    abs_file_path = os.path.join(script_dir, 'INPUT_DATA/' + SHP_FILENAMES[level])
    groupedPoints = LineGroupingFromSHP(abs_file_path, MINIMALDIST)
    
    
# ------ Calculate bounding box of openings and create opening objects --------
    # openings is CLASS OPENINGS to be used for contour reconstruction
    abs_file_path = os.path.join(script_dir, 'INPUT_DATA/' + DXF_FILENAMES[level])
    openings = calcOpeningBoundingBox(abs_file_path, WINDOW_LAYER_NAME, DOOR_LAYER_NAME)



# ---------- Reconstruct contours from wall lines and opening lines -----------
    # Nodes is openings that can be successfully reconstructed and exported into TABLE NODES
    # contourPoint is the corner points of the ways to be exported into TABLE WAYS representing contours
    contourPoints, Nodes=ContourReconstruction00(groupedPoints, openings, AVG_WALL_THICKNESS, verbose)




# ------------------ Find level shell and filter out columns ------------------
    maxS=0
    indx_Shell=-1
    indx_Columns=[]
    
    for i in range(0, len(contourPoints)):
        if len(contourPoints[i])>2:
            S=Polygon(contourPoints[i]).area
            if S<1000000: # contours with area smaller than 1 m2 are considered columns
                indx_Columns.append(i)
            elif S>maxS:
                maxS=S
                indx_Shell=i
    levelshell=contourPoints[indx_Shell]
    
    indx_ToDelete=indx_Columns+[indx_Shell]
    indx_ToDelete.sort()

    for i in range(0, len(indx_ToDelete)):
        contourPoints.pop(indx_ToDelete[i]-i)
#------------------------------------------------------------------------------       




# ----------------------- Export data into database ---------------------------  
    if EXPORT_DATA_INTO_DATABASE==True:
        
        
        # Insert the level relation record into TABLE RELATION  
        tag="hstore(array['type','name','height','level'],array['level', '" + FLOORNAMES[level] + "Level" + "', '" + str(LEVELHEIGHT) +"','" + str(level) + "'])"
        cur.execute("INSERT INTO relations (id, tags) VALUES (" + str(levelID) + ", " + tag + ");")    
        conn.commit()
        
        
        # Insert the relation between this level and the building into TABLE RELATION_MEMBERS
        cur.execute("INSERT INTO relation_members (relation_id, member_id, member_type, member_role) VALUES (" + str(0) + ", " + str(levelID) + ", 'R', 'level_" + str(level) + "');")
        conn.commit()   



        # Insert doors and windows into TABLE NODES
        for i in range(0, len(Nodes)):
            if Nodes[i].type==0: # doors
                tag="hstore(array['door','level', 'width','height'],array['yes','" + str(level) + "','" + str(Nodes[i].length/1000) + "','" + str(DOORHEIGHT) +"'])"
            else: # windows
                tag="hstore(array['window','level', 'width','height','breast'],array['yes','" + str(level) + "','"  + str(Nodes[i].length/1000) + "','" + str(WINDOWHEIGHT) +"','"+str(WINDOWBREAST)+"'])"
                
            cur.execute("INSERT INTO nodes (id, tags, geom) VALUES (" + str(numNODES+i) + ", " + tag + ", ST_GeomFromText('POINT(" + str(Nodes[i].center.y/1000) + " " + str(Nodes[i].center.x/1000) + ")', " + str(sourceCRS_EPSG) + "));")         
            conn.commit()
        
        # Insert level shell of this floor into TABLE WAYS
        geom="'LINESTRING("
        for i in range(0, len(levelshell)):
            geom=geom+str(levelshell[i][1]/1000)+" "+str(levelshell[i][0]/1000)+","
        geom=geom+str(levelshell[0][1]/1000)+" "+str(levelshell[0][0]/1000)+")'"
        
        tag="hstore(array['name','height','level'],array['" + FLOORNAMES[level] + "Shell" + "','" + str(LEVELHEIGHT) +"','" + str(level) + "'])"
        cur.execute("INSERT INTO ways (id, tags, linestring) VALUES (" + str(numWAYS) + ", " + tag + ", ST_GeomFromText(" + geom + ", " + str(sourceCRS_EPSG) + "));")
        
        # Insert the relation between the shell and this level into TABLE RELATION_MEMBERS
        cur.execute("INSERT INTO relation_members (relation_id, member_id, member_type, member_role) VALUES (" + str(level+1) + ", " + str(numWAYS) + ", 'W', 'shell');")         
        conn.commit()    
        

        # Insert ways of rooms into TABLE WAYS
        for i in range(0, len(contourPoints)):
            if len(contourPoints[i])>0:
                geom="'LINESTRING("
                for j in range(0, len(contourPoints[i])):
                    pt=contourPoints[i][j]
                    geom=geom+str(contourPoints[i][j][1]/1000)+" "+str(contourPoints[i][j][0]/1000)+","
            geom=geom+str(contourPoints[i][0][1]/1000)+" "+str(contourPoints[i][0][0]/1000)+")'"
            
            tag="hstore(array['name','buildingpart','height','indoor'],array['Room "+str(level)+ "-" + str(i) + "','room','" + str(ROOMHEIGHT) +"','yes'])"
            cur.execute("INSERT INTO ways (id, tags, linestring) VALUES (" + str(numWAYS+i+1) + ", " + tag + ", ST_GeomFromText(" + geom + ", " + str(sourceCRS_EPSG) + "));")
            # Insert the relation between the way and this level into TABLE RELATION_MEMBERS
            cur.execute("INSERT INTO relation_members (relation_id, member_id, member_type, member_role) VALUES (" + str(levelID) + ", " + str(numWAYS+i+1) + ", 'W', 'buildingpart');")
            conn.commit()
        
        levelID=levelID+1
        numNODES=numNODES+len(Nodes)
        numWAYS=numWAYS+len(contourPoints)+1
#------------------------------------------------------------------------------
            

# ------------------ Close communication with the database --------------------
if EXPORT_DATA_INTO_DATABASE==True:
    cur.close()
    conn.close()
#------------------------------------------------------------------------------
       
    
    
    
#------------------------------------------------------------------------------
print '#-----------------------------'
print 'finished!'
print 'executing time:', time.time() - start_time, 'seconds'
print time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
print '#-----------------------------'
