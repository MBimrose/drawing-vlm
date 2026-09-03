from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
rib_height = 6.0
rib_offset = 5.0
slot_width = 4.0
slot_length = 40.0
hole_diameter = 4.0
hole_offset = 15.0
edge_fillet = 1.5
rib_fillet = 0.8
chamfer_size = 0.5

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), edge_fillet)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_width - 2*rib_offset, plate_height - 2*rib_offset, rib_height)
solid_body = solid_body + rib
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), rib_fillet)

slot = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(slot_length, slot_width, rib_height)
solid_body = solid_body - slot

hole_r = hole_diameter / 2
hole_h = plate_thickness + rib_height + 10
for y in [-(plate_height/2 - hole_offset), (plate_height/2 - hole_offset)]:
    solid_body = solid_body - Pos(-plate_width/2, y, 0) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
    solid_body = solid_body - Pos(plate_width/2, y, 0) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
for x in [-(plate_width/2 - hole_offset), (plate_width/2 - hole_offset)]:
    solid_body = solid_body - Pos(x, -plate_height/2, 0) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)
    solid_body = solid_body - Pos(x, plate_height/2, 0) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")