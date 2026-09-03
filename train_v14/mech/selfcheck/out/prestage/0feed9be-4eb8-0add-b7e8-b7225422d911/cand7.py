from build123d import *

outer_radius = 30
inner_radius = 20
sleeve_length = 70
fillet_radius = 2
hole_diameter = 5
hole_offset_radius = 25

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, sleeve_length))
            l3 = Line(l2@1, (inner_radius, sleeve_length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

for x, y in [(hole_offset_radius, 0), (-hole_offset_radius, 0)]:
    solid_body = solid_body - Pos(x, y, sleeve_length/2) * Cylinder(hole_diameter/2, sleeve_length + 10)

part = solid_body
part.name = "sleeve_with_holes"
export_step(part, "output.step")