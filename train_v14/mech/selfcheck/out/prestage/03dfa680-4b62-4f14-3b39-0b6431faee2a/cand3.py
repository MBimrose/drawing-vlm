from build123d import *

base_width = 80.0
base_depth = 80.0
base_thickness = 8.0
pocket_width = 50.0
pocket_depth = 50.0
pocket_height = 6.0
rib_width = 12.0
rib_depth = 12.0
rib_height = 6.0
rib_offset = 10.0
hole_diameter = 3.0
slot_width = 5.0
slot_length = 30.0
chamfer_size = 0.8

rib_positions = [
    (base_width/2 - rib_offset, base_depth/2 - rib_offset),
    (-base_width/2 + rib_offset, base_depth/2 - rib_offset),
    (-base_width/2 + rib_offset, -base_depth/2 + rib_offset),
    (base_width/2 - rib_offset, -base_depth/2 + rib_offset)
]

solid = Box(base_width, base_depth, base_thickness)
solid = solid - Pos(0, 0, base_thickness - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
for x, y in rib_positions:
    solid = solid + Pos(x, y, base_thickness/2 + rib_height/2) * Box(rib_width, rib_depth, rib_height)
for x, y in rib_positions:
    solid = solid - Pos(x, y, rib_height/2) * Cylinder(hole_diameter/2, base_thickness + rib_height + 2)
solid = solid - Pos(0, -base_depth/2 + slot_width/2, 0) * Box(slot_length, slot_width, base_thickness + rib_height + 2)
solid = chamfer(solid.edges(), chamfer_size)

part = solid
part.name = "base_plate_with_pocket_ribs"
export_step(part, "output.step")