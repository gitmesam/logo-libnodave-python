#!/usr/bin/python
#LOGO.py
#2013-04-12
###########################################################
# -comunicacio entre python i logo! oba7-                 #
#Aquest script es un refregit elaborat per:               #
#   Jaume Nogues (jnogues@gmail.com),                     #
#basat en la llibreria libnodave creada per:              #
#   (C) Thomas Hergenhahn (thomas.hergenhahn@web.de)      #
#amb afegits de:                                          #
#   Wouter D'Haeseleer (https://github.com/netdata)       #
#i amb la colaborarcio de ask, membre del forum de Siemens#
###########################################################

import ctypes
import os
import time

def int_to_bitarr(integer):
    string = bin(integer)[2:]
    arr = list()
    
    for bit in xrange(8 - len(string)):
        arr.append(0)
    
    for bit in string:
        arr.append(int(bit))
    
    arr.reverse()
    return arr

def bitarr_to_int(bitarr):
    str_bitarr = list()
    bitarr.reverse()
    for elem in bitarr:
        str_bitarr.append(str(elem))
    print str_bitarr
    string = ''.join(str_bitarr)
    return int(string,2)

class Logo:
    
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.ph = 0         # Porthandle
        self.di = 0         # Dave Interface Handle
        self.dc = 0
        self.res = 1
        self.rack = 1       # Verbindung nicht O.K. bei Start
        self.slot = 0
        self.mpi = 2
        self.dave = ""
        self.daveDB = 132
        self.daveFlags = 131
        self.daveOutputs = 130
        self.daveInputs = 129

        self.daveDI = 133 # instance data blocks
        self.daveLocal = 134 # not tested 
        self.daveV = 135 # don't know what it is
        self.daveCounter = 28 # S7 counters
        self.daveTimer = 29 # S7 timers
        self.daveCounter200 = 30 # IEC counters (200 family)
        self.daveTimer200 = 31 # IEC timers (200 family) 
        
        #ruta de la libreria libnodave
        Dateipfad = os.getcwd() 
        DLL_LOC = Dateipfad + '/' + ('libnodave.so')
              
        if os.name == 'nt':
            DLL_LOC = Dateipfad + '/' + ('libnodave.dll')
            self.dave = ctypes.windll.LoadLibrary(DLL_LOC)
        if os.name == 'posix':
            DLL_LOC = Dateipfad + '/' + ('libnodave.so')
            self.dave = ctypes.cdll.LoadLibrary(DLL_LOC)
        print
        print "********   LOGO.py Version 2013_04_12  **************"
        print "*****************************************************"
        print "  Sistema Operativo: ",os.name
        print "  llibreria libnodave:   ",DLL_LOC
        print "*****************************************************"
            
    #****************************************************************   
    def connect(self):        
        # Open connection
        print 
        print "- Intentant connectar..."
        self.ph = self.dave.openSocket(self.port, self.ip)
        if self.ph > 0:
            print "- Port Handle O.K."
        else:
            print "- Port Handle N.O.K."
            
        # Dave Interface handle
        self.di = self.dave.daveNewInterface(self.ph, self.ph, 'IF1', 0,  122 , 2)
        print "- Dave Interface Handle :", self.di
        
        # Init Adapter
        self.res = self.dave.daveInitAdapter(self.di)
        if self.res == 0:
            print "- Init Adapter O.K."
        else:
            print "- Init Adapter N.O.K."
            
        # dave Connection
        self.dc = self.dave.daveNewConnection(self.di, self.mpi, self.rack, self.slot )       # daveNewConnection(di, MPI, rack, slot)
        print "- Dave Connection: ", self.dc
        
        self.res = self.dave.daveConnectPLC(self.dc)
        self.dave.daveSetTimeout(self.di, 5000000)
        print "- res: ", self.res
        
        
    def readbytes(self, db, start, len):
        print "- read"
        print        
        if self.res == 0:
            rd = self.dave.daveReadBytes(self.dc, self.daveDB ,db,start,len, 0)
            
            print "ReadBytes: ",len #+ str(self.res)
            for z in range(len):                
                a=self.dave.daveGetU16(self.dc)
                print z," ", a
            
        else:
            print "Bitte erst Verbindung Ueber C O N N E C T  aufbauen"
            
    def writebytes(self, db, wort, wert):
        print "- write"
        print
        u=self.dave.daveSwapIed_16(wert) 
        buffer = ctypes.c_int(int(u))
        buffer_p =  ctypes.pointer(buffer)        
        a = self.dave.daveWriteManyBytes(self.dc, self.daveDB, db, wort,2, buffer_p)

    
    def disconnect(self):
        self.dave.daveDisconnectPLC(self.dc);
        self.dave.closePort(self.ph)
        print
        print "- Verbindung zur SPS beendet"
        
            
    def writeOutputs(self, db, wort, wert):
        print "- write"
        print
        u=self.dave.daveSwapIed_16(wert) 
        buffer = ctypes.c_int(int(u))
        buffer_p =  ctypes.pointer(buffer)        
        a = self.dave.daveWriteManyBytes(self.dc, self.daveOutputs, db, wort,2, buffer_p)

  
    def read_bytes(self, area, db, start, len):    
        res = self.dave.daveReadBytes(self.dc, area, db, start, len, 0)
        if res == 0:
            return True
        return False
    
    #***********************************************************************************************      
    #******************************** READ IN BYTE FORMAT ******************************************
    #INPUTS
    def get_input_byte(self, input_):
        if self.read_bytes(self.daveInputs, 0, input_, 1):
            return self.dave.daveGetU8(self.dc)
        return -1

    #OUTPUTS
    def get_output_byte(self, output):
        if self.read_bytes(self.daveOutputs, 0, output, 1):
            return self.dave.daveGetU8(self.dc)
        return -1
    #MARKS
    def get_marker_byte(self, marker):
        if self.read_bytes(self.daveFlags, 0, marker, 1):
            return self.dave.daveGetU8(self.dc)
        return -1

    #VM
    def get_vm_byte(self, vm):
        if self.read_bytes(self.daveDB, 1, vm, 1):
            return self.dave.daveGetU8(self.dc)
        return -1


    #******************************** READ IN BIT FORMAT ******************************************
    #INPUTS
    def get_input(self, input, byte): 
        m_byte = self.get_input_byte(input)
        if m_byte >= 0:
            byte_arr = int_to_bitarr(m_byte)
            return byte_arr[byte]
        return False

    #OUTPUTS
    def get_output(self, output, byte): 
        m_byte = self.get_output_byte(output)
        if m_byte >= 0:
            byte_arr = int_to_bitarr(m_byte)
            return byte_arr[byte]
        return False

    def outputs(self):
        Q1 = self.get_output(0,0)
        Q2 = self.get_output(0,1)
        Q3 = self.get_output(0,2)
        Q4 = self.get_output(0,3)

        print "Q1 : " + str(Q1)
        print "Q2 : " + str(Q2)
        print "Q3 : " + str(Q3)
        print "Q4 : " + str(Q4)
    
    #MARKS 
    def get_marker(self, marker, byte):
        m_byte = self.get_marker_byte(marker)
        if m_byte >= 0:
            byte_arr = int_to_bitarr(m_byte)
            return byte_arr[byte]
        return False    

    #VM
    def get_vm(self, vm, byte):
        m_byte = self.get_vm_byte(vm)
        if m_byte >= 0:
            byte_arr = int_to_bitarr(m_byte)
            return byte_arr[byte]
        return False    

    #******************************** READ IN WORD & DOUBLE FORMAT ******************************************
    #VM
    def get_vm_word(self, vm):
        if self.read_bytes(self.daveDB, 1, vm, 2):
            return self.dave.daveGetU16(self.dc)
        return -1
        
    def get_vm_double(self, vm):
        if self.read_bytes(self.daveDB, 1, vm, 4):
            return self.dave.daveGetU32(self.dc)
        return -1           

    #******************************** WRITE IN BYTE FORMAT ******************************************
    #OUTPUTS
    def write_output_byte(self, output, value):
        buffer = ctypes.c_byte(int(value))        
        buffer_p = ctypes.pointer(buffer)
        self.dave.daveWriteBytes(self.dc, self.daveOutputs, 0, output, 1, buffer_p)

    #MARKS
    def write_marker_byte(self, mark, value):
        buffer = ctypes.c_byte(int(value))        
        buffer_p = ctypes.pointer(buffer)
        self.dave.daveWriteBytes(self.dc, self.daveFlags, 0, mark, 1, buffer_p)
    
    #VM
    def write_vm_byte(self, vm, value):
        buffer = ctypes.c_byte(int(value))        
        buffer_p = ctypes.pointer(buffer)
        self.dave.daveWriteBytes(self.dc, self.daveDB, 1, vm, 1, buffer_p)

    #******************************** WRITE IN BIT FORMAT ******************************************
    #OUTPUTS
    def set_output_bit(self, output, position):
        self.dave.daveSetBit(self.dc , self.daveOutputs, 0, output, position)
    def clear_output_bit(self, output, position):
        self.dave.daveClrBit(self.dc, self.daveOutputs, 0, output, position)
    
    #VM
    def set_vm_bit(self, vm, position):
        self.dave.daveSetBit(self.dc , self.daveDB, 1, vm, position)

    def clear_vm_bit(self, vm, position):
        self.dave.daveClrBit(self.dc, self.daveDB, 1, vm, position)
 
    #MARKS
    def set_mark_bit(self, mark, position):
        self.dave.daveSetBit(self.dc , self.daveFlags, 0, mark, position)
    def clear_mark_bit(self, mark, position):
        self.dave.daveClrBit(self.dc, self.daveFlags, 0, mark, position)

    
    #***********************************************************************************************
    
#********************** end class Logo ********************************************

    
plc = Logo("192.168.4.201",102)
plc.connect()
#plc.write_vm_byte(150,16)
#time.sleep(5)

#plc.set_vm_bit(0,1)
#plc.write_vm_byte(0,0)
#plc.get_marker(0,0)
#plc.get_marker_byte(0)
#plc.get_marker_byte_dict(0)
#plc.get_marker_byte_list(0)
#plc.get_counter_value(1)
#plc.get_counters()
#plc.write_marker_byte(0,0)
#plc.write_marker_byte(2,255)
plc.write_output_byte(0,255)
#plc.write_output_byte(1,0)


#plc.stop_plc()
#plc.clear_vm_bit(0,0)
#plc.clear_vm_bit(0,1)
#plc.write_output_byte(0,255)
#plc.write_output_byte(1,255)
#plc.write_marker_byte(0,255)
#plc.write_marker_byte(2,0)
#plc.write_vm_byte(0,1)
#plc.outputs()
plc.disconnect()












