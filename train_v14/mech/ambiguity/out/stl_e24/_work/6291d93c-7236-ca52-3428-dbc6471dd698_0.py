from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
rib_height = 3.0
rib_offset = 2.0
slot_width = 6.0
slot_depth = 10.0
slot_offset_x = 10.0
slot_offset_y = 5.0
hole_diameter = 4.0
countersink_diameter = 8.0
countersink_angle = 90.0
hole_offset_x = 10.0
hole_offset_y = 10.0
chamfer_size = 1.0
fillet_radius = 0.5

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, plate_thickness/2) * Box(plate_length - 2*rib_offset, plate_width - 2*rib_offset, rib_height)
result = base + rib

slot = Pos(plate_length/2 - slot_offset_x, plate_width/2 - slot_offset_y, -plate_thickness/2) * Box(slot_width, slot_depth, plate_thickness)
result = result - slot

hole = Pos(hole_offset_x, hole_offset_y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)
result = result - hole

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

part = result
part.name = "plate_with_rib_slot_and_hole"
export_step(part, "output.step")