from build123d import *

side_length = 80.0
thickness = 10.0
rib_width = 5.0
rib_height = 3.0
hole_diameter = 12.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(side_length, 3)
    extrude(amount=thickness)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch(Plane.XY.offset(thickness)) as rs:
        RegularPolygon(side_length + 2 * rib_width, 3)
    extrude(amount=rib_height)

solid_body = solid_body + rib_p.part

total_height = thickness + rib_height
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(hole_diameter / 2, total_height + 2)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "triangular_plate_with_rib"
export_step(part, "output.step")