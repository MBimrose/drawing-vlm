from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
cutout_length = 30.0
cutout_width = 20.0
slot_length = 20.0
slot_width = 5.0
slot_offset_from_edge = 10.0
hole_diameter = 4.0
hole_offset = 8.0
fillet_radius = 2.0
rib_height = 2.0
rib_thickness = 2.0
rib_spacing = 15.0

result = Box(plate_length, plate_width, plate_thickness)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

result = result - Box(cutout_length, cutout_width, plate_thickness)

slot_center_x = -plate_length/2 + slot_offset_from_edge + slot_length/2
result = result - Pos(slot_center_x, 0, 0) * Box(slot_length, slot_width, plate_thickness)

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

num_ribs = int((plate_length - 2*hole_offset) // rib_spacing) + 1
for i in range(num_ribs):
    x_pos = -plate_length/2 + hole_offset + i * rib_spacing
    rib = Pos(x_pos, 0, -plate_thickness/2 + rib_height/2) * Box(rib_thickness, plate_width - 2*hole_offset, rib_height)
    result = result + rib

part = result
part.name = "plate_with_cutouts_and_ribs"
export_step(part, "output.step")