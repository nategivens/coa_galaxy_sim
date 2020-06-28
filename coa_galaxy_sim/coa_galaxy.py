class COA_Galaxy:
    def __init__(self, radius, height, h_zone_inner_radius=None, h_zone_outer_radius=None):
        self.radius = radius
        self.height = height
        self.h_zone_inner_radius = h_zone_inner_radius
        self.h_zone_outer_radius = h_zone_outer_radius
        self.stars = []

    def add_star(self, star=None, ):
        self.stars.append(star)