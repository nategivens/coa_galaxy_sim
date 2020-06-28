import time
import sys
import numpy as np
import pandas as pd
import datetime
from pathlib import Path
import yaml
from coa_galaxy import COA_Galaxy
from coa_star import COA_Star


def write_output_data(base_path, output_data_fname, distances):
    file_path = (base_path / 'data' / output_data_fname)
    columns = ['iter_'+str(x) for x in range(distances.shape[1])]
    distances_df = pd.DataFrame(data=distances, columns=columns)
    distances_df.to_csv(file_path, index_label='Star')


def write_output_log(base_path, sim_vars):
    file_path = (base_path / 'logs' / sim_vars['log_filename'])
    with open(file_path, 'w') as outfile:
        yaml.dump(sim_vars, outfile, default_flow_style=False)


def main(**kwargs):
    # set default simulation parameters
    # TODO: Create a default sim .csv, populate with values, and read from there.
    sim_vars = {
        'galaxy_radius': 50000,
        'galaxy_height': 1000,
        'h_zone_inner_radius': 22000,
        'h_zone_outer_radius': 29000,
        'num_stars': 65536,
        'iterations': 32,
        'save_output': True
    }
    # override default simulation parameters if arguments are passed in from commandline
    for key, value in kwargs.items():
        if key in sim_vars:
            try:
                sim_vars[key] = int(kwargs[key])
            except ValueError:
                print('Non-integer value {0} passed for {1} parameter. Aborting.'.format(value, key))
                sys.exit()
    # add additional sim_vars (that I don't want to possibly be set from commandline)
    sim_vars['elapsed_time'] = None
    sim_vars['finished_datetime'] = None
    sim_vars['data_filename'] = None
    sim_vars['log_filename'] = None
    # TODO: Test validity of sim_vars (iterations>0, inner_radius<outer_radius, outer_radius < galaxy_radius, etc)
    # Create an XxI array where X = num_stars and I = iterations.
    # This will store the distance from each start to its closest neighbor for a given iteration.
    nearest_neighbor_distances = np.array(
        [[float('inf') for i in range(sim_vars['iterations'])] for x in range(sim_vars['num_stars'])])
    # Start the timer.
    start_time = time.time()
    for iteration in range(sim_vars['iterations']):
        print('Starting iteration {0}.'.format(str(iteration)))
        # Create a new COA_Galaxy object.
        galaxy = COA_Galaxy(radius=sim_vars['galaxy_radius'],
                            height=sim_vars['galaxy_height'],
                            h_zone_inner_radius=sim_vars['h_zone_inner_radius'],
                            h_zone_outer_radius=sim_vars['h_zone_outer_radius'])
        # Populate the COA_Galaxy with COA_Star objects.
        galaxy.stars = [COA_Star(galaxy=galaxy, is_homestar=True) for i in range(sim_vars['num_stars'])]
        # Calculate all star distances and save closest neighbor distance star for each
        for x in range(sim_vars['num_stars']):
            nearest_neighbor_distance = float('inf')
            for y in range(sim_vars['num_stars']):
                if x != y:
                    neighbor_distance = galaxy.stars[x].compute_distance(galaxy.stars[y])
                    if neighbor_distance < nearest_neighbor_distance:
                        nearest_neighbor_distances[x][iteration] = neighbor_distance
                        nearest_neighbor_distance = neighbor_distance
    # End the timer and calculate elapsed time.
    end_time = time.time()
    output_datetime = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    elapsed_time = end_time - start_time
    print('Simulation complete. Total elapsed time = {0}.'.format(str(elapsed_time)))
    if sim_vars['save_output']:
        print('Writing data.')
        base_path = Path(__file__).parent.resolve().parent.resolve()
        sim_vars['elapsed_time'] = elapsed_time
        sim_vars['finished_datetime'] = output_datetime
        sim_vars['run_type'] = 'serial'
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
