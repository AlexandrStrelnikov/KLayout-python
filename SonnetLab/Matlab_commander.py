import sys
import time

import csv

import pya
from math import sqrt, cos, sin, tan, atan2, pi, copysign
from pya import Point, DPoint, Vector, DVector, DSimplePolygon, SimplePolygon, DPolygon, Polygon, Region
from pya import Trans, DTrans, CplxTrans, DCplxTrans, ICplxTrans

from ClassLib import *
from sonnetLab.matlabClient import  MatlabClient

import numpy as np

import socket
import struct
import numpy as np

class SonnetLab( MatlabClient ):
    def __init__(self, host="localhost", port=MatlabClient.MATLAB_PORT ):
        super(SonnetLab,self).__init__()
    
    def clear( self ):    
        self._clear()
        
    def set_boxProps( self, dim_X_nm, dim_Y_nm, cells_X_num, cells_Y_num ):
        self._set_boxProps( dim_X_nm/1e3, dim_Y_nm/1e3, cells_X_num, cells_Y_num )
        
    def set_ABS_sweep(self, start_f, stop_f ):
        self._set_ABS_sweep( start_f, stop_f )
    
    def send_element( self, el_class_obj ):
        el = el_class_obj # name alias
        
        if( el.metal_region.size() > 1 ):
            print( "region consists of more than 1 polygon, this is not supported yet")
            return None
        
        poly = el.metal_region[0].dup() # the only polygon in the region
        sonnet_port_connection_indexes = []
        self.send_polygon( poly, el.sonnet_port_edge_indexes )
        
    def send_polygon( self, polygon, connections=None, port_edges_indexes=None ):
        pts_x = np.zeros(polygon.num_points(), dtype=np.int32 )
        pts_y = np.zeros(polygon.num_points(), dtype=np.int32 )
        print( "Sending polygon", " ", connections )
        if( port_edges_indexes is not None ):
            print( "port edges indexes passing is not implemented yet." )
            raise NotImplementedError
        
        port_edges_indexes = []    
        
        for i,edge in enumerate(polygon.each_edge()):
            pts_x[i] = pt.x/1e3
            pts_y[i] = pt.y/1e3
            
            if( prev_pt is None ):,  
                prev_pt = pt
                continue
                
            for conn_pt in connections:
                dr = conn_pt - prev_pt
                a = pt - prev_pt
                h = abs(dr.x*a.y - dr.y*a.x)/np.sqrt(a.x**2 + a.y**2)
                if( h < 10 ): # distance from connection point to the edge in nm
                    port_edges_indexes.append(i-1)
                    print(conn_pt, prev_pt, pt)
                    break
                    
            prev_pt = pt
            
        print( port_edges_indexes )
        self._send_polygon( pts_x,pts_y, port_edges_indexes )
        
    def send_cell_layer( self, cell, layer_i, port_connections ):
        r_cell = Region( cell.begin_shapes_rec( layer_i ) )
        for poly in r_cell:
            self.send_polygon( poly, port_connections )
    
    def start_simulation( self ):
        self._send_simulate()
    
    def visualize_sever( self ):
        self._visualize_sever()
    
    def release( self ):
        print( "closing connection" )
        self._send( CMD.CLOSE_CONNECTION )
        print("connection closed\n")
        self._close()

if __name__ == "__main__":
# getting main references of the application
    app = pya.Application.instance()
    mw = app.main_window()
    lv = mw.current_view()
    cv = None
    
    #this insures that lv and cv are valid objects
    if( lv == None ):
        cv = mw.create_layout(1)
        lv = mw.current_view()
    else:
        cv = lv.active_cellview()

# find or create the desired by programmer cell and layer
    layout = cv.layout()
    layout.dbu = 0.001
    if( layout.has_cell( "testScript") ):
        pass
    else:
        cell = layout.create_cell( "testScript" )
    
    info = pya.LayerInfo(1,0)
    info2 = pya.LayerInfo(2,0)
    layer_ph = layout.layer( info )
    layer_el = layout.layer( info2 )

    # clear this cell and layer
    cell.clear()

    # setting layout view  
    lv.select_cell(cell.cell_index(), 0)
    lv.add_missing_layers()

    ### DRAW SECTION START ###
    origin = DPoint(0,0)
    
    X_SIZE = 100e3
    Y_SIZE = 100e3
    
    # Chip drwaing START #
    cpw_pars = CPWParameters( 14.5e3, 6.7e3 ) 
    box = pya.Box( 0,0, X_SIZE,Y_SIZE )
    cell.shapes( layer_ph ).insert( box )
    
    cop = CPW_RL_Path( DPoint(0,Y_SIZE/2), "LRL", cpw_pars, 10e3, [X_SIZE/2,Y_SIZE/2], np.pi/2 )
    cop.place( cell, layer_ph )
    ports = [cop.start, cop.end]
    ### DRAW SECTION END ###
    
    lv.zoom_fit()
    from sonnetLab.cMD import CMD
    ### MATLAB COMMANDER SECTION START ###
    ml_terminal = SonnetLab()
    print("starting connection...")
    ml_terminal._send( CMD.SAY_HELLO )
    ml_terminal.clear()
    ml_terminal.set_boxProps( X_SIZE,Y_SIZE, 200,100 )
    print( "sending cell and layer" )
    ml_terminal.send_cell_layer( cell, layer_ph, ports )
    ml_terminal.set_ABS_sweep( 1, 10 )
    print( "simulating..." )
    ml_terminal.start_simulation()
    print("visualizing...")
    ml_terminal.visualize_sever()
    file_name = ml_terminal.read_line()#.decode("ASCII")
    ml_terminal.release()

    with open(file_name,"r") as csv_file:
        rows = np.array( list(csv.reader(csv_file))[8:], dtype=np.float64 )
        
    ### MATLAB COMMANDER SECTION END ###