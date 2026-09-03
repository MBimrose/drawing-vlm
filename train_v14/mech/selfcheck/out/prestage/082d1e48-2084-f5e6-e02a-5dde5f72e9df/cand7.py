from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 4.0
cavity_length = 50.0
cavity_width = 30.0
cavity_depth = block_height - wall_thickness
hole_diameter = 8.0
hole_depth = 20.0
fillet_radius = 2.0
rib_thickness = 3.0
rib_width = 10.0
rib_height = 5.0
rib_offset = 5.0

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

cavity = Pos(0, 0, block_height - cavity_depth/2) * Box(cavity_length, cavity_width, cavity_depth)
base = base - cavity

hole = Pos(block_length/2 - hole_depth/2, 0, block_height/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
base = base - hole

rib = Box(rib_width, rib_thickness, rib_height)
rib_positions = [
    (-block_length/2 + rib_offset + rib_width/2, -block_width/2 + rib_offset + rib_thickness/2),
    ( block_length/2 - rib_offset - rib_width/2, -block_width/2 + rib_offset + rib_thickness/2),
    (-block_length/2 + rib_offset + rib_width/2,  block_width/2 - rib_offset - rib_thickness/2),
    ( block_length/2 - rib_offset - rib_width/2,  block_width/2 - rib_offset - rib_thickness/2),
]
for x, y in rib_positions:
    base = base + Pos(x, y, rib_height/2) * rib

part = base
part.name = "block_with_cavity_hole_ribs"
export_step(part, "output.step")