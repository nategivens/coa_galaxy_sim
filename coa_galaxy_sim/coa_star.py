import math
import numpy as np


class COA_Star:
    def __init__(self, galaxy, x=None, y=None, z=None, is_homestar=False):
        self.galaxy = galaxy
        self.x = x
        self.y = y
        self.z = z
        self.is_homestar = is_homestar
        if self.x is None or self.y is None or self.z is None:
            self.new_star_coords()

    def new_star_coords(self):
        r = self.get_star_radius()
        theta = np.random.random() * 2 * math.pi
        self.x = r * np.cos(theta)
        self.y = r * np.sin(theta)
        self.z = (np.random.random() * self.galaxy.height) - (self.galaxy.height / 2)

    def get_star_radius(self):
        inner_radius = 0
        outer_radius = self.galaxy.radius
        if self.is_homestar:
            inner_radius = self.galaxy.h_zone_inner_radius
            outer_radius = self.galaxy.h_zone_outer_radius
        star_radius = 0
        while star_radius < inner_radius or star_radius > outer_radius:
            star_radius = outer_radius * math.sqrt(np.random.random())
        return star_radius

    def __str__(self):
        return 'x: {0}, y: {1}, z: {2}'.format(str(self.x), str(self.y), str(self.z))

    def compute_distance(self, other_star):
        return ((self.x - other_star.x) ** 2 + (self.y - other_star.y) ** 2 + (self.z - other_star.z) ** 2) ** 0.5
