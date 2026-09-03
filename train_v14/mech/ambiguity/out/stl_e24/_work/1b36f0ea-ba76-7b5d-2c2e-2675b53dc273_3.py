from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 5.0
rib_height = 2.0
rib_width = 8.0
slot_length = 30.0
slot_width = 6.0
slot_spacing = 12.0
num_slots = 3
fillet_radius = 1.0
hole_diameter = 4.0
hole_offset = 10.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_depth, plate_thickness)
rib1 = Pos(0, 0, plate_thickness + rib_height/2) * Box(rib_width, plate_depth - 2*hole_offset, rib_height)
rib2 = Pos(0, 0, plate_thickness + rib_height/2) * Box(plate_width - 2*hole_offset, rib_width, rib_height)

result = base + rib1 + rib2

slot_start_x = -((num_slots - 1) * (slot_width + slot_spacing)) / 2
for i in range(num_slots):
    x = slot_start_x + i * (slot_width + slot_spacing)
    slot = Pos(x, 0, (plate_thickness + rib_height)/2) * Box(slot_width, slot_length, plate_thickness + rib_height)
    result = result - slot

hole_positions = [
    (-plate_width/2 + hole_offset, -plate_depth/2 + hole_offset),
    (plate_width/2 - hole_offset, -plate_depth/2 + hole_offset),
    (-plate_width/2 + hole_offset, plate_depth/2 - hole_offset),
    (plate_width/2 - hole_offset, plate_depth/2 - hole_offset),
]
for x, y in hole_positions:
    hole = Pos(x, y, (plate_thickness + rib_height)/2) * Cylinder(hole_diameter/2, plate_thickness + rib_height)
    result = result - hole

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "plate_with_ribs_slots_holes"
export_step(part, "output.step")