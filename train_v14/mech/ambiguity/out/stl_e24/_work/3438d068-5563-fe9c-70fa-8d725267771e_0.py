from build123d import *

outer_diameter = 30.0
inner_diameter = 12.0
collar_length = 15.0
groove_width = 2.0
groove_depth = 1.5
chamfer_size = 1.0
set_screw_hole_diameter = 5.0
set_screw_offset = 3.0
tab_width = 4.0
tab_height = 2.0
tab_thickness = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=collar_length)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, collar_length / 2) * Cylinder(inner_radius, collar_length)

groove_r = inner_radius - groove_width / 2.0
groove_z = collar_length - groove_depth / 2.0
solid_body = solid_body - Pos(0, 0, groove_z) * Cylinder(groove_r, groove_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

hole_r = set_screw_hole_diameter / 2.0
hole_tool = Rot(0, 90, 0) * Cylinder(hole_r, outer_diameter + 2)
for y in [set_screw_offset, -set_screw_offset]:
    solid_body = solid_body - Pos(outer_radius, y, collar_length / 2) * hole_tool

tab = Pos(outer_radius, 0, collar_length / 2) * Box(tab_width, tab_thickness, tab_height)
solid_body = solid_body + tab

part = solid_body
part.name = "collar_with_groove_and_tabs"
export_step(part, "output.step")