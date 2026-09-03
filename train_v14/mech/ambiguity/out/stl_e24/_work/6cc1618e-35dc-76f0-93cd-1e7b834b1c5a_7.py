from build123d import *
import math

outer_radius = 30.0
inner_radius = 20.0
length = 80.0
relief_groove_depth = 2.0
relief_groove_width = 5.0
relief_groove_position = 30.0
set_screw_diameter = 5.0
set_screw_head_diameter = 9.0
set_screw_head_depth = 3.0
set_screw_position = 25.0
chamfer_size = 1.0
rib_thickness = 2.0
rib_height = 10.0
rib_position = 40.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, length))
            l2 = Line(l1 @ 1, (outer_radius, length))
            l3 = Line(l2 @ 1, (outer_radius, 0))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

groove = Pos(0, 0, relief_groove_position + relief_groove_width / 2) * Cylinder(inner_radius + relief_groove_depth, relief_groove_width)
solid_body = solid_body - groove

set_screw_x = outer_radius - set_screw_head_depth - 2.0
set_screw_z = length - set_screw_position
shaft_hole = Pos(set_screw_x, set_screw_head_depth / 2, set_screw_z) * Rot(90, 0, 0) * Cylinder(set_screw_diameter / 2, set_screw_head_depth)
solid_body = solid_body - shaft_hole
csk_cone = Pos(set_screw_x, set_screw_head_depth / 2, set_screw_z) * Rot(90, 0, 0) * Cone(set_screw_head_diameter / 2, set_screw_diameter / 2, set_screw_head_depth)
solid_body = solid_body - csk_cone

rib = Pos(inner_radius - rib_thickness / 2, 0, rib_position) * Box(rib_thickness, rib_height, rib_thickness)
solid_body = solid_body + rib

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_groove_and_rib"
export_step(part, "output.step")