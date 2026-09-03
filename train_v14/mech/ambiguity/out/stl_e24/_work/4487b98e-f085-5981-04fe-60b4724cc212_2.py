from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
corner_fillet_radius = 5.0
central_hole_diameter = 30.0
slot_length = 20.0
slot_width = 8.0
slot_offset_from_end = 10.0
slot_offset_from_side = 15.0
rib_height = 2.0
rib_width = 6.0
chamfer_distance = 0.8

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness)

slot_x = plate_length/2 - slot_offset_from_end - slot_length/2
slot_y = plate_width/2 - slot_offset_from_side - slot_width/2
for sx, sy in [(slot_x, slot_y), (-slot_x, slot_y), (slot_x, -slot_y), (-slot_x, -slot_y)]:
    solid_body = solid_body - Pos(sx, sy, 0) * Box(slot_length, slot_width, plate_thickness)

rib_outer = Cylinder(central_hole_diameter/2 + rib_width, rib_height)
rib_inner = Cylinder(central_hole_diameter/2, rib_height)
rib = Pos(0, 0, -plate_thickness) * (rib_outer - rib_inner)
solid_body = solid_body + rib

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "plate_with_slots_and_rib"
export_step(part, "output.step")