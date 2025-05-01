'''
called by generate_replicates.sh for use with a slurm HPC cluster

runs the CC3D cellular-potts agent-based mechanistic model with parameters and output paths specified by the generate_replicates.sh script
'''

import os
import datetime
from os.path import dirname, join, expanduser
from cc3d.CompuCellSetup.CC3DCaller import CC3DCaller
import numpy as np
import gc
import argparse
import logging

logging.basicConfig(filename='simulation.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def call_cc3d_sim(model_params, workspace_path, n):
    sim_fname = os.path.join(dirname(__file__), 'Angiogenesis3.cc3d')
    rep_name = f'simulation_{n}_contact_{model_params[0]}_decay_{model_params[1]}' #name of the output file
    workspace_path = os.path.join(workspace_path, rep_name)
    os.makedirs(workspace_path, exist_ok=True)

    cc3d_caller = CC3DCaller(
        cc3d_sim_fname=sim_fname,
        sim_input=model_params,
        output_dir=workspace_path)
    
    try:
        ret_value = cc3d_caller.run()
        logging.info(f'Simulation {n} completed successfully from call_cc3d_sim function')
    except Exception as e:
        logging.error(f'Error in simulation {n}: {str(e)}')
    finally:
        del cc3d_caller
        gc.collect()
    return

def main(contact_param, decay_param, simulation_rep, output_path, workspace_dump_path):
    model_params = [contact_param, decay_param, simulation_rep, output_path]

    logging.info(f'Starting simulation {simulation_rep} with contact_param {contact_param} and decay_param {decay_param}')

    try:
        call_cc3d_sim(model_params, workspace_dump_path, simulation_rep)
    except Exception as e:
        logging.error(f'Error in simulation {simulation_rep} with contact_param {contact_param} and decay_param {decay_param}: {str(e)}')
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('contact_param', type=float, help='EC_Med_Contact parameter')
    parser.add_argument('decay_param', type=float, help='VEGF_decay parameter')
    parser.add_argument('simulation_rep', type=int, help='Simulation replicate number')
    parser.add_argument('output_path', type=str, help='Path to output zarr file')
    parser.add_argument('workspace_dump_path', type=str, help='Path to workspace dump directory')
    args = parser.parse_args()

    main(args.contact_param, args.decay_param, args.simulation_rep, args.output_path, args.workspace_dump_path)