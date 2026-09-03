from build123d import *

outer_radius = 30.0
inner_radius = 20.0
bracket_height = 70.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset = 25.0
pocket_width = 12.0
pocket_height = 20.0
pocket_depth = 8.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, bracket_height))
            l2 = Line(l1 @ 1, (outer_radius, bracket_height))
            l3 = Line(l2 @ 1, (outer_radius, 0))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

for x, y in [(-hole_offset, 0), (hole_offset, 0)]:
    solid_body = solid_body - Pos(x, y, bracket_height/2) * Cylinder(hole_diameter/2, bracket_height)

pocket_box = Box(pocket_depth, pocket_width, pocket_height)
pocket_box = Pos(outer_radius - pocket_depth/2, 0, bracket_height/2) * pocket_box
solid_body = solid_body - pocket_box

part = solid_body
part.name = "bracket"
export_step(part, "output.step")