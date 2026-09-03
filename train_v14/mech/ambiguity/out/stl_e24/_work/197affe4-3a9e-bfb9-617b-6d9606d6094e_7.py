from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 5.0
cavity_length = 40.0
cavity_width = 30.0
cavity_depth = block_height - wall_thickness
chamfer_size = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 35.0
rib_thickness = 3.0

result = Box(block_length, block_width, block_height)

cavity = Pos(0, 0, block_height - cavity_depth/2) * Box(cavity_length, cavity_width, cavity_depth)
result = result - cavity

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width)
    result = result - hole

rib1 = Pos(0, 0, rib_thickness/2) * Box(block_length, rib_thickness, rib_thickness)
rib2 = Pos(0, 0, rib_thickness/2) * Box(rib_thickness, block_width, rib_thickness)
result = result + rib1 + rib2

top_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "block_with_cavity_and_ribs"
export_step(part, "output.step")