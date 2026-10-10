from build123d import *

outer_diameter = 60.0
inner_diameter = 30.0
collar_length = 20.0
slot_width = 12.0
slot_length = 40.0
chamfer_distance = 0.8
fillet_radius = 1.0
set_screw_diameter = 5.0
set_screw_offset = 10.0
pocket_width = 8.0
pocket_depth = 4.0
pocket_length = 12.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, collar_length) - Cylinder(inner_radius, collar_length)
solid_body = solid_body - Box(slot_length, slot_width, collar_length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

solid_body = solid_body - Pos(set_screw_offset, 0, 0) * Cylinder(set_screw_diameter / 2, collar_length)

pocket = Box(pocket_width, pocket_depth, pocket_length)
for angle in [0, 90, 180, 270]:
    solid_body = solid_body - Rot(0, 0, angle) * Pos(outer_radius - pocket_depth / 2, 0, 0) * pocket

part = solid_body
part.name = "collar_with_slot_and_pockets"
export_step(part, "output.step")