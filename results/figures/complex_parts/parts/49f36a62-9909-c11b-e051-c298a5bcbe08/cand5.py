from build123d import *

inner_diameter = 19.6
wall_thickness = 9.2
outer_diameter = inner_diameter + 2 * wall_thickness
collar_length = 15.0
split_gap = 1.0
chamfer_size = 0.4
hole_diameter = 3.0
hole_spacing = 20.0
rib_height = 2.0
rib_thickness = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, collar_length) - Cylinder(inner_radius, collar_length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

slot = Pos(0, 0, collar_length / 2.0) * Box(split_gap, outer_diameter, wall_thickness + 0.2)
solid_body = solid_body - slot

for x, y in [(-hole_spacing / 2.0, 0), (hole_spacing / 2.0, 0)]:
    solid_body = solid_body - Pos(x, y, collar_length / 2.0) * Cylinder(hole_diameter / 2.0, collar_length + 1)

rib = Pos(0, 0, collar_length / 2.0 + rib_height / 2.0) * Box(rib_thickness, outer_diameter - 2 * wall_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "split_collar"
export_step(part, "output.step")