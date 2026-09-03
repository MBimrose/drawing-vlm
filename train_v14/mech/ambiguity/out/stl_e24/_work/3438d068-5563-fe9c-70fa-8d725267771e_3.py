from build123d import *

outer_diameter = 30.0
inner_diameter = 12.0
collar_length = 15.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
hole_diameter = 5.0
hole_offset = 6.0
chamfer_distance = 1.0
rib_width = 4.0
rib_height = 3.0
rib_thickness = 2.0
relief_groove_width = 2.0
relief_groove_depth = 1.5

solid_body = Cylinder(outer_diameter / 2.0, collar_length)
solid_body = solid_body - Cylinder(inner_diameter / 2.0, collar_length)

for y_off in [hole_offset, -hole_offset]:
    hole = Pos(0, y_off, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2.0, outer_diameter + 2.0)
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

rib = Pos(outer_diameter / 2.0, 0, 0) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

groove = Pos(0, 0, collar_length / 2.0 - relief_groove_depth / 2.0) * Cylinder(inner_diameter / 2.0 + relief_groove_width, relief_groove_depth)
solid_body = solid_body - groove

part = solid_body
part.name = "collar_with_rib_and_groove"
export_step(part, "output.step")