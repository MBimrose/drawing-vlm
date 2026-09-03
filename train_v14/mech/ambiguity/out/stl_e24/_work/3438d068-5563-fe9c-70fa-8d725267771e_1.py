from build123d import *

outer_diameter = 30.0
inner_diameter = 12.0
collar_length = 15.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
hole_diameter = 5.0
hole_spacing = 6.0
chamfer_size = 1.0
rib_height = 2.0
rib_width = 3.0
rib_thickness = 1.0
pocket_depth = 3.0

solid_body = Cylinder(outer_diameter / 2.0, collar_length)
solid_body = solid_body - Cylinder(inner_diameter / 2.0, collar_length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for y in [-hole_spacing / 2.0, hole_spacing / 2.0]:
    solid_body = solid_body - Pos(outer_diameter / 2.0, y, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2.0, outer_diameter)
    solid_body = solid_body - Pos(-outer_diameter / 2.0, y, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2.0, outer_diameter)

rib = Pos(outer_diameter / 2.0 + rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_height, rib_width)
solid_body = solid_body + rib

pocket = Pos(0, 0, collar_length / 2.0 - pocket_depth / 2.0) * Cylinder(inner_diameter / 2.0, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "collar_with_rib"
export_step(part, "output.step")