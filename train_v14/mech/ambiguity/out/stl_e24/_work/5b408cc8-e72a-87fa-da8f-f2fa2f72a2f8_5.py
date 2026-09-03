from build123d import *

outer_width = 60.0
outer_height = 20.0
arc_height = 15.0
length = 30.0
wall_thickness = 2.5
hole_diameter = 4.0
hole_spacing = 15.0
hole_count = 3
fillet_radius = 2.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_width, 0))
            l2 = Line(l1 @ 1, (outer_width, outer_height))
            arc = ThreePointArc(l2 @ 1, (outer_width / 2, outer_height + arc_height), (0, outer_height))
            l3 = Line(arc @ 1, (0, 0))
        make_face()
    extrude(amount=length)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

for i in range(hole_count):
    x = outer_width / 2 + (i - (hole_count - 1) / 2) * hole_spacing
    y = outer_height / 2
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, length * 2)

part = solid_body
part.name = "shelled_box_with_holes"
export_step(part, "output.step")