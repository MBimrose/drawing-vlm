from build123d import *

plate_length = 100.0
plate_width = 30.0
plate_thickness = 5.0
slot_length = 30.0
slot_width = 10.0
hole_diameter = 5.1
hole_spacing = 20.0
hole_count = 4
chamfer_distance = 2.0
rib_length = 20.0
rib_width = 5.0
rib_thickness = plate_thickness

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

slot = Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - slot

rib_left = Pos(-plate_length/2 + rib_length/2, -plate_width/2 + rib_width/2, 0) * Box(rib_length, rib_width, rib_thickness)
rib_right = Pos(plate_length/2 - rib_length/2, -plate_width/2 + rib_width/2, 0) * Box(rib_length, rib_width, rib_thickness)
solid_body = solid_body + rib_left + rib_right

for i in range(hole_count):
    x = -plate_length/2 + 10 + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness)

part = solid_body
part.name = "plate_with_slot_ribs_and_holes"
export_step(part, "output.step")