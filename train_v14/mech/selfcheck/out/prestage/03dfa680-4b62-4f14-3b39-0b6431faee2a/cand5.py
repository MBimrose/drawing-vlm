from build123d import *

base_width = 80.0
base_depth = 80.0
base_thickness = 8.0
pocket_width = 50.0
pocket_depth = 50.0
pocket_depth_cut = 4.0
pad_size = 12.0
pad_height = 6.0
pad_offset = 10.0
pad_hole_diameter = 3.0
slot_width = 20.0
slot_depth = 5.0
fillet_radius = 2.0

base = Box(base_width, base_depth, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

pocket = Pos(0, 0, base_thickness - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
base = base - pocket

pad_positions = [
    (base_width/2 - pad_offset - pad_size/2, base_depth/2 - pad_offset - pad_size/2),
    (-base_width/2 + pad_offset + pad_size/2, base_depth/2 - pad_offset - pad_size/2),
    (-base_width/2 + pad_offset + pad_size/2, -base_depth/2 + pad_offset + pad_size/2),
    (base_width/2 - pad_offset - pad_size/2, -base_depth/2 + pad_offset + pad_size/2),
]

for x, y in pad_positions:
    pad = Pos(x, y, base_thickness/2 + pad_height/2) * Box(pad_size, pad_size, pad_height)
    base = base + pad

for x, y in pad_positions:
    hole = Pos(x, y, base_thickness/2 + pad_height/2) * Cylinder(pad_hole_diameter/2, pad_height + 0.2)
    base = base - hole

slot = Pos(0, -base_depth/2 + slot_depth/2, base_thickness/2) * Box(slot_width, slot_depth, base_thickness)
base = base - slot

part = base
part.name = "base_plate_with_pockets_and_pads"
export_step(part, "output.step")