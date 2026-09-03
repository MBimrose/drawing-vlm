from build123d import *

outer_radius = 30
inner_radius = 20
length = 70
groove_depth = 5
groove_width = 5
groove_position = 30
fillet_radius = 2
hole_diameter = 5
hole_offset = 25

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, length))
            l2 = Line(l1@1, (outer_radius, length))
            l3 = Line(l2@1, (outer_radius, 0))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

groove_cyl = Pos(0, 0, groove_position - groove_width / 2) * Cylinder(inner_radius - groove_depth, groove_width)
solid_body = solid_body - groove_cyl

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

hole1 = Pos(outer_radius - 5, 0, hole_offset) * Cylinder(hole_diameter / 2, length * 2)
hole2 = Pos(-(outer_radius - 5), 0, hole_offset) * Cylinder(hole_diameter / 2, length * 2)
solid_body = solid_body - hole1 - hole2

part = solid_body
part.name = "sleeve_with_groove_and_holes"
export_step(part, "output.step")