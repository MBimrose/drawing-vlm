from build123d import *

outer_radius = 30.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
length = 80.0
rib_width = 6.0
rib_height = 8.0
rib_count = 12
shaft_radius = 10.0
shaft_length = 30.0
chamfer_size = 1.0

import math

# Hollow cylinder (outer minus inner)
result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

# Add ribs around the outer surface
rib_radius = outer_radius + rib_height / 2
for i in range(rib_count):
    angle_deg = i * 360.0 / rib_count
    angle_rad = math.radians(angle_deg)
    px = rib_radius * math.cos(angle_rad)
    py = rib_radius * math.sin(angle_rad)
    rib = Pos(px, py, 0) * Rot(0, 0, angle_deg) * Box(rib_width, rib_height, length)
    result = result + rib

# Add shaft at the bottom
shaft = Pos(0, 0, -length/2 - shaft_length/2) * Cylinder(shaft_radius, shaft_length)
result = result + shaft

# Chamfer the bottom edge of the shaft
bottom_face = result.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
result = chamfer(bottom_edges, chamfer_size)

part = result
part.name = "hollow_cylinder_with_ribs_and_shaft"
export_step(part, "output.step")