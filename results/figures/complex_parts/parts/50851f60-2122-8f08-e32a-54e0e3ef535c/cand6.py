from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 30.0
height = 20.0
rib_height = 2.0
rib_width = 5.0
slot_width = 4.0
slot_height = 12.0
slot_depth = 8.0
chamfer_size = 1.0
pocket_width = 10.0
pocket_height = 4.0
pocket_depth = 8.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

rib = Cylinder(outer_radius, rib_height) - Cylinder(outer_radius - rib_width, rib_height)
rib = Pos(0, 0, height/2 - rib_height/2) * rib
result = result + rib

pocket = Box(pocket_width, pocket_height, pocket_depth)
pocket = Pos(inner_radius - pocket_depth/2, 0, height/2 - pocket_depth/2) * pocket
result = result - pocket

for angle in [0, 90, 180, 270]:
    slot = Box(slot_depth, slot_width, slot_height)
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth/2, 0, 0) * slot
    result = result - slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "hollow_cylinder_with_rib_pockets_slots"
export_step(part, "output.step")