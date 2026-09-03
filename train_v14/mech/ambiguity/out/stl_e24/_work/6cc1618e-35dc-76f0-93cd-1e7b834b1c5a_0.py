from build123d import *

outer_radius = 30.0
inner_radius = 20.0
length = 80.0
groove_width = 30.0
groove_depth = 2.0
set_screw_diameter = 5.0
set_screw_offset = 25.0
set_screw_depth = 8.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, length))
            l2 = Line(l1@1, (inner_radius, length))
            l3 = Line(l2@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

groove_cyl = Pos(0, 0, length - groove_width) * Cylinder(inner_radius + groove_depth, groove_width)
solid_body = solid_body - groove_cyl

set_screw_cyl = Pos(outer_radius - set_screw_depth/2, set_screw_depth/2, length/2 + set_screw_offset) * Rot(90, 0, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - set_screw_cyl

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_groove_and_setscrew"
export_step(part, "output.step")