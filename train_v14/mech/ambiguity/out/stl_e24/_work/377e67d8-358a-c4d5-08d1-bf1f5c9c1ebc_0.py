from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 10.0
slot_width = 30.0
slot_length = 60.0
rib_width = 5.0
rib_height = 5.0
hole_diameter = 6.0
hole_offset = 10.0
counterbore_diameter = 10.0
counterbore_depth = 4.0
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, plate_thickness/2 - rib_height/2) * Box(rib_width, plate_width - 2*hole_offset, rib_height)
result = base + rib

slot_cut = Box(slot_width, slot_length, plate_thickness + 2)
result = result - slot_cut

hole_positions = [
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
]

for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 2)
    result = result - Pos(x, y, -plate_thickness/2 + counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_rib_slot_and_holes"
export_step(part, "output.step")