from build123d import *

plate_width = 80.0
plate_height = 25.0
plate_thickness = 8.0
slot_width = 40.0
slot_height = plate_height * 0.6
rib_width = 4.0
rib_height = 6.0
rib_spacing = 10.0
rib_count = int((plate_width - 2 * rib_spacing) / rib_spacing) + 1
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset = 8.0

solid_body = Box(plate_width, plate_thickness, plate_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

slot = Box(slot_width, plate_thickness, slot_height)
solid_body = solid_body - slot

rib = Box(rib_width, rib_height, rib_width)
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    solid_body = solid_body + Pos(x, plate_thickness / 2 + rib_height / 2, rib_width / 2) * rib

hole = Rot(90, 0, 0) * Cylinder(hole_diameter / 2, plate_thickness + 2)
for x, z in [(-plate_width / 2 + hole_offset, -plate_height / 4),
             (-plate_width / 2 + hole_offset, plate_height / 4),
             (plate_width / 2 - hole_offset, -plate_height / 4),
             (plate_width / 2 - hole_offset, plate_height / 4)]:
    solid_body = solid_body - Pos(x, 0, z) * hole

part = solid_body
part.name = "plate_with_slot_ribs_holes"
export_step(part, "output.step")