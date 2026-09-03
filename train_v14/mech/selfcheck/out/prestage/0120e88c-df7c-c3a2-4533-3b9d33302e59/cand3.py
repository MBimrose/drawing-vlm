from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
rib_width = 10.0
rib_height = 60.0
rib_thickness = 5.0
slot_width = 20.0
slot_depth = 2.0
slot_offset_from_top = 5.0
hole_diameter = 4.0
cbore_diameter = 7.0
cbore_depth = 3.0
hole_spacing = 30.0
chamfer_size = 1.0

base = Box(plate_width, plate_height, plate_thickness)
rib = Pos(-plate_width/2 + rib_width/2, 0, 0) * Box(rib_width, rib_height, rib_thickness)
solid_body = base + rib

slot_y = plate_height/2 - slot_offset_from_top - slot_depth/2
slot = Pos(0, slot_y, plate_thickness/2) * Box(slot_width, slot_depth, plate_thickness)
solid_body = solid_body - slot

for x in [-hole_spacing, 0, hole_spacing]:
    solid_body = solid_body - Pos(x, 0, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)
    solid_body = solid_body - Pos(x, 0, plate_thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)

bottom_face = solid_body.faces().sort_by(Axis.Y)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")