from build123d import *

outer_radius = 30.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
length = 80.0
rib_width = 6.0
rib_height = 8.0
rib_count = 12
blind_hole_diameter = 12.0
blind_hole_depth = 20.0
boss_radius = 10.0
boss_height = 30.0
chamfer_size = 1.0

import math

# Shell: outer cylinder minus inner cylinder
result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

# Add ribs around outer surface
for i in range(rib_count):
    angle_deg = i * 360.0 / rib_count
    angle_rad = math.radians(angle_deg)
    px = (outer_radius + rib_height / 2) * math.cos(angle_rad)
    py = (outer_radius + rib_height / 2) * math.sin(angle_rad)
    rib = Pos(px, py, 0) * Rot(0, 0, angle_deg) * Box(rib_width, rib_height, length)
    result = result + rib

# Add boss at bottom face
boss = Pos(0, 0, -length / 2 - boss_height / 2) * Cylinder(boss_radius, boss_height)
result = result + boss

# Blind hole at top face
hole = Pos(0, 0, length / 2 - blind_hole_depth / 2) * Cylinder(blind_hole_diameter / 2, blind_hole_depth)
result = result - hole

# Chamfer bottom edges
bottom_face = result.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
result = chamfer(bottom_edges, chamfer_size)

part = result
part.name = "ribbed_shell_with_boss"
export_step(part, "output.step")