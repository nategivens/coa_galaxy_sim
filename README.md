# coa_galaxy_sim

## Overview
This project contains astronomical simulations that I use for world-building in my sci-fi setting: Chronicles of Ascension. In the stories I am writing, an ancient space-faring race seeded 65,536 star systems in the [Milky Way Galaxy's habitable zone](https://en.wikipedia.org/wiki/Galactic_habitable_zone) with intelligent life. I wanted to know how far apart these homesystems would be, which turned out to be a difficult problem to handle analytically. So I decided to write a simulation. This, my first sim (closest_neighbor_star_serial) was born. This simulation ran slowly (about 2 hours per iteration) so I created a parallelized version of it (closest_neighbor_star_parallel). I'll provide additional info on both of these below. In the future, I hope to add more simulations to this repo to answer questions I run into as an author.

## closest_neighbor_star_serial
Each iteration of this simulation creates a COA_Galaxy object and populates it with COA_Star objects. It then finds the distance from each of the randomly-positioned stars to its nearest neighbor. Upon completion of a successful run, a log file is written to the `logs` directory and the output is written to the `data` directory. Each output file is a .csv containing one column for each iteration and one row for each star. The data in the table is the distance (in light years) to that star's nearest neighbor. 

The important parameters are:

|Parameter|Description|Default|
|---|---|---|
|num_stars|The number of stars to be generated|65,536|
|iterations|The number of iterations to run. Each iteration generates a completely new set of stars|32|
|galaxy_height|The height of the galaxy in light years. Stars are uniformly distributed vertically within this region.|1,000|
|h_zone_inner_radius|The inner radius of the galaxy's habitable zone in light years. Stars are generated within the inner and outer radii.|22,000|
|h_zone_outer_radius|The outer radius of the galaxy's habitable zone in light years. Stars are generated within the inner and outer radii.|29,000|

All of these default variables can be overridden at the commandline. To run a serial simulation with defults:

```python closest_neighbor_star_serial.py```

But if you want to change the number of iterations to two, you'd instead execute:

```python closest_neighbor_star_serial.py iterations=2```

On my desktop computer with in i7-6700K CPU, an iteration with the default parameters takes about 2 hours to run, so the whole simulation (32 iterations) takes about 64 hours to complete. If you want to try it out, you can run with a lower number of stars and a lower number of iterations to get much faster results. If you run it with about 100 stars or fewer, results will take just a couple of seconds per iteration.

## closest_neighbor_star_parallel
The logic of this version is identical to the serial version, but it uses [concurrent.futures](https://docs.python.org/3.7/library/concurrent.futures.html) to run the iterations in parallel. This results in a speedup of 4x on my machine, which has four cores available to run parallel iterations of the simulation. This reduces the total simulation time with default parameters from about 64 to 16 hours.

## COA_Galaxy Class
The COA_Galaxy class doesn't do much at this point, other than simply store the galaxy-specific parameters (like galaxy_heigh, h_zone_inner_radius, h_zone_outer_radius) and a list of all the stars. It has an add_star method, but I'm not presently using it.

## COA_Star Class
The COA_Star class has a little bit more going on than the COA_Galaxy class. Each COA_Star retains a link to its COA_Galaxy along with it's coordinates (x, y, z where 0,0,0 is the galactic center). In addition, COA_Star has logic for randomly generating x,y,z coordinates so that stars are uniformly distributed within the habitable zone. It also has a simple method for computing Euclidean distance between any two stars.

## Analysis
I keep all the analysis of the simulation output separate from the simulation itself. That analysis is conducted in Jupyter notebooks (because it's easy to get pretty charts that way), and I'll be committing some of that work soon.
