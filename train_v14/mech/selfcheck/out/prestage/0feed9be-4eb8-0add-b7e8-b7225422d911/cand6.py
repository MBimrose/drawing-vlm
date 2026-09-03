from build123d import *

outer_radius = 30.0
inner_radius = 20.0
height = 70.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 50.0
pocket_diameter = 20.0
pocket_depth = 5.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, height))
            l2 = Line(l1@1, (inner_radius, height))
            l3 = Line(l2@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

pocket = Pos(0, 0, height - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)
solid_body = solid_body - pocket

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    hole = Pos(x, y, height/2) * Cylinder(hole_diameter/2, height + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "revolved_ring_with_pocket_and_holes"
export_step(part, "output.step")