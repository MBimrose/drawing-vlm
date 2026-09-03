from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 40.0
pocket_width = 30.0
hole_diameter = 6.0
countersink_diameter = 10.0
countersink_angle = 82.0
hole_offset_x = 25.0
hole_offset_y = 20.0
slot_length = 20.0
slot_width = 4.0
slot_offset = 25.0
rib_width = 10.0
rib_height = 3.0
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges(), chamfer_size)

base = base - Box(pocket_length, pocket_width, plate_thickness)

for x, y in [(-hole_offset_x, -hole_offset_y), (hole_offset_x, -hole_offset_y),
             (-hole_offset_x, hole_offset_y), (hole_offset_x, hole_offset_y)]:
    base = base - Pos(x, y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)

for y in [slot_offset, -slot_offset]:
    base = base - Pos(0, y, 0) * Box(slot_length, slot_width, plate_thickness)

rib = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width - 2*slot_offset, rib_height)
base = base + rib

part = base
part.name = "plate_with_pocket_holes_slots_rib"
export_step(part, "output.step")