from build123d import *
import math

side_length = 60.0
thickness = 10.0
rib_height = 3.0
rib_width = 5.0
hole_diameter = 12.0
chamfer_distance = 0.5
tri_height = math.sqrt(3) / 2 * side_length
outer_side = side_length + 2 * rib_width
outer_tri_height = math.sqrt(3) / 2 * outer_side
v1 = (-side_length / 2, -tri_height / 3)
v2 = (side_length / 2, -tri_height / 3)
v3 = (0, 2 * tri_height / 3)
outer_v1 = (-outer_side / 2, -outer_tri_height / 3)
outer_v2 = (outer_side / 2, -outer_tri_height / 3)
outer_v3 = (0, 2 * outer_tri_height / 3)

with BuildPart() as p:
    with BuildSketch() as s:
        Polygon(v1, v2, v3)
    extrude(amount=thickness)
base = p.part

with BuildPart() as p2:
    with BuildSketch() as s2:
        Polygon(outer_v1, outer_v2, outer_v3)
    extrude(amount=rib_height)
rib = Pos(0, 0, thickness) * p2.part

solid_body = base + rib
solid_body = solid_body - Cylinder(hole_diameter / 2, thickness + rib_height + 10)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "triangular_plate_with_rib"
export_step(part, "output.step")