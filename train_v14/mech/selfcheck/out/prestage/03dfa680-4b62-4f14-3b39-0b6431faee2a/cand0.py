from build123d import *

plate_width = 80.0
plate_depth = 80.0
plate_thickness = 8.0
pocket_width = 50.0
pocket_depth = 50.0
pocket_depth_cut = 4.0
corner_pad_size = 12.0
corner_pad_height = 6.0
corner_hole_diameter = 3.0
slot_length = 30.0
slot_width = 5.0
slot_offset_from_edge = 2.0
chamfer_size = 0.5

base = Box(plate_width, plate_depth, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

pocket = Pos(0, 0, plate_thickness - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
base = base - pocket

pad_positions = [
    (plate_width/2 - corner_pad_size/2, plate_depth/2 - corner_pad_size/2),
    (-plate_width/2 + corner_pad_size/2, plate_depth/2 - corner_pad_size/2),
    (-plate_width/2 + corner_pad_size/2, -plate_depth/2 + corner_pad_size/2),
    (plate_width/2 - corner_pad_size/2, -plate_depth/2 + corner_pad_size/2),
]

for x, y in pad_positions:
    pad = Pos(x, y, plate_thickness/2 + corner_pad_height/2) * Box(corner_pad_size, corner_pad_size, corner_pad_height)
    base = base + pad

for x, y in pad_positions:
    hole = Pos(x, y, plate_thickness/2 + corner_pad_height/2) * Cylinder(corner_hole_diameter/2, corner_pad_height + 0.2)
    base = base - hole

slot_y = -plate_depth/2 + slot_offset_from_edge + slot_width/2
slot = Pos(0, slot_y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness + 0.2)
base = base - slot

part = base
part.name = "plate_with_pocket_pads_and_slot"
export_step(part, "output.step")