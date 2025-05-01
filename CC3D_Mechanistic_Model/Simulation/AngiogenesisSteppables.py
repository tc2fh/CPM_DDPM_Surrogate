
from cc3d.core.PySteppables import *
from cc3d import CompuCellSetup
from cc3d.CompuCellSetup import persistent_globals as pg
import numpy as np
import zarr
import os


PythonCall = False #set to 1 if running from python, 0 if running from CC3D

mcs_start = 0 #start saving at 10000 mcs
mcs_end = 20001 #end simulation at 20001 mcs, arange stops at mcs_end - 1
save_step = 100 #save every 100 mcs
timesteps = np.arange(mcs_start, mcs_end, save_step)

localtesting = False


class AngiogenesisSteppable(SteppableBasePy):

    def __init__(self,frequency=1):

        SteppableBasePy.__init__(self,frequency)

    def start(self):
        
        # if localtesting:
        #     global EC_Med_Contact
        #     global VEGF_decay

        #     EC_Med_Contact = self.get_xml_element('EC_Med_Contact')
        #     EC_Med_Contact.cdata = float(0)

        #     VEGF_decay = self.get_xml_element('VEGF_decay')
        #     VEGF_decay.cdata = float(0.05)

        if PythonCall:

            #values2pass should contain 4 values: float: EC_Med_Contact, float: VEGF_decay, int: RunNumber, str: OutputPath

            values2pass = pg.input_object
            global RunNumber
            global OutputPath
            # if localtesting == False:
            #     global VEGF_decay
            #     global EC_Med_Contact
           
            EC_Med_Contact = self.get_xml_element('EC_Med_Contact')
            EC_Med_Contact.cdata = float(values2pass[0])

            VEGF_decay = self.get_xml_element('VEGF_decay')
            VEGF_decay.cdata = float(values2pass[1])

            RunNumber = int(values2pass[2]) #run number for naming file
            OutputPath = values2pass[3] #path to folder where output zarr file will be saved

            #create zarr file with zipstore backend
            zarrpath = os.path.join(OutputPath, f'contact_{values2pass[0]}_decay_{values2pass[1]}_simulation_{RunNumber}.zarr.zip')
            self.store = zarr.ZipStore(zarrpath, mode='w')
            self.root = zarr.group(store=self.store)

            #pre-allocate arrays for fgbg (cell segmentation)
            self.fgbg_array = self.root.zeros("fgbg", shape=(len(timesteps), self.dim.y, self.dim.x), chunks=(1, self.dim.y, self.dim.x), dtype=bool)


    def step(self,mcs):

        if localtesting and mcs == 0:
            print('mcs = 0, EC_Med_Contact = ',EC_Med_Contact.cdata,' VEGF_decay = ',VEGF_decay.cdata)

        if PythonCall:
            if mcs in timesteps:
                #write to zarr with zipstore backend
                shape = (self.dim.y,self.dim.x) #images are in z,y,x convention, or depth, height, width
                fgbg_data = np.zeros(shape,dtype=bool)
                for x, y, z in self.every_pixel():
                    cell = self.cell_field[x, y, z]
                    if cell: fgbg_data[y,x] = True
                
                # Write data to the pre-allocated arrays in the zarr file
                mcs_index = np.where(timesteps == mcs)[0][0]
                self.fgbg_array[mcs_index] = fgbg_data

    def finish(self):
        if PythonCall:
            self.store.close()
        

    def on_stop(self):
        if PythonCall:
            self.store.close()
        return


        