from build123d import *

outer_radius = 28.0
inner_radius = 22.0
body_height = 45.0
shoulder_height = 10.0
central_hole_diameter = 10.0
relief_width = 12.0
relief_depth = 6.0
chamfer_distance = 2.0
fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, body_height - shoulder_height))
            l3 = Line(l2 @ 1, (inner_radius, body_height - shoulder_height))
            l4 = Line(l3 @ 1, (inner_radius, body_height))
            l5 = Line(l4 @ 1, (0, body_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

solid_body = solid_body - Cylinder(central_hole_diameter / 2, body_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

relief_box = Pos(outer_radius - relief_depth / 2, 0, 0) * Box(relief_depth, body_height * 2, outer_radius * 2)
solid_body = solid_body - relief_box

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "revolved_body_with_relief"
export_step(part, "output.step")