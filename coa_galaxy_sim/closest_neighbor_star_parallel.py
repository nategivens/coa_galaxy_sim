import time
import sys
import copy
import concurrent.futures
from pathlib import Path
import datetime
import yaml
import pandas as pd
from coa_galaxy import COA_Galaxy
from coa_star import COA_Star


def write_output_data(base_path, output_data_fname, distances):
    file_path = (base_path / 'data' / output_data_fname)
    columns = ['iter_'+str(x) for x in range(len(distances))]
    distances_df = pd.DataFrame(distances)
    # This transposition step is necessary in the parallel version
    # because we're using a list of lists instead of numpy array
    distances_df = distances_df.transpose()
    distances_df.columns = columns
    distances_df.to_csv(file_path, index_label='Star')


def write_output_log(base_path, sim_vars):
    file_path = (base_path / 'logs' / sim_vars['log_filename'])
    with open(file_path, 'w') as outfile:
        yaml.dump(sim_vars, outfile, default_flow_style=False)


def run_iteration(iteration_vars):
    # Create a list to store the nearest neighbor distances
    nearest_neighbor_distances = [float('inf') for x in range(iteration_vars['num_stars'])]
    # Create a new COA_Galaxy object.
    galaxy = COA_Galaxy(radius=iteration_vars['galaxy_radius'],
                        height=iteration_vars['galaxy_height'],
                        h_zone_inner_radius=iteration_vars['h_zone_inner_radius'],
                        h_zone_outer_radius=iteration_vars['h_zone_outer_radius'])
    # Populate the COA_Galaxy with COA_Star objects.
    galaxy.stars = [COA_Star(galaxy=galaxy, is_homestar=True) for i in range(iteration_vars['num_stars'])]
    for x in range(iteration_vars['num_stars']):
        nearest_neighbor_distance = float('inf')
        for y in range(iteration_vars['num_stars']):
            if x != y:
                neighbor_distance = galaxy.stars[x].compute_distance(galaxy.stars[y])
                if neighbor_distance < nearest_neighbor_distance:
                    nearest_neighbor_distances[x] = neighbor_distance
                    nearest_neighbor_distance = neighbor_distance
    return nearest_neighbor_distances


def main(**kwargs):
    start_time = time.time()
    # set default simulation parameters
    # TODO: Create a default sim .csv, populate with values, and read from there.
    sim_vars = {
        'galaxy_radius': 50000,
        'galaxy_height': 1000,
        'h_zone_inner_radius': 22000,
        'h_zone_outer_radius': 29000,
        'num_stars': 65536,
        'iterations': 32,
        'save_output': 1
    }
    # override default simulation parameters if arguments are passed in from commandline
    for key, value in kwargs.items():
        if key in sim_vars:
            try:
                sim_vars[key] = int(kwargs[key])
            except ValueError:
                print('Non-integer value {0} passed for {1} parameter. Aborting.'.format(value, key))
                sys.exit()
    sim_vars_list = [None] * sim_vars['iterations']
    # create a list with deepcopies of sim_vars to feed to our parallel threads
    for i in range(sim_vars['iterations']):
        sim_vars_list[i] = copy.deepcopy(sim_vars)
        sim_vars_list[i]['iteration'] = i
    # Note that this list of lists is transposed vs. the numpy array in the serial version of the sim
    nearest_neighbor_distances = [[float('inf') for i in range(sim_vars['num_stars'])] for x in range(sim_vars['iterations'])]
    current_iteration = 0
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for nearest_neighbor_distances_part in executor.map(run_iteration, sim_vars_list):
            nearest_neighbor_distances[current_iteration] = nearest_neighbor_distances_part
            current_iteration = current_iteration + 1
    end_time = time.time()
    # add additional sim_vars (that I don't want to possibly be set from commandline)
    sim_vars['elapsed_time'] = None
    sim_vars['finished_datetime'] = None
    sim_vars['data_filename'] = None
    sim_vars['log_filename'] = None
    output_datetime = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    elapsed_time = end_time - start_time
    print('Simulation complete. Total elapsed time = {0}.'.format(str(elapsed_time)))
    if sim_vars['save_output'] == 1:
        print('Writing data.')
        base_path = Path(__file__).parent.resolve().parent.resolve()
        sim_vars['elapsed_time'] = elapsed_time
        sim_vars['finished_datetime'] = output_datetime
        sim_vars['run_type'] = 'parallel'
        sim_vars['data_filename'] = 'closest_neighbor_star_sim_data-' + output_datetime + '.csv'
        sim_vars['log_filename'] = 'closest_neighbor_star_sim_log-' + output_datetime + '.yaml'
        write_output_data(base_path, sim_vars['data_filename'], nearest_neighbor_distances)
        write_output_log(base_path, sim_vars)
        print('Finished writing data.')


if __name__ == '__main__':
    # convert command line args to kwargs
    keyval_args = [keyval for keyval in sys.argv[1:] if '=' in keyval]
    split_keyval_args = (keyval.split('=') for keyval in keyval_args)
    console_kwargs = {key: value for key, value in split_keyval_args}
    main(**console_kwargs)