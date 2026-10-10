from build123d import *
import math

triangle_side = 80.0
plate_thickness = 10.0
rib_height = 3.0
rib_offset = 5.0
central_hole_diameter = 12.0
vertex_hole_diameter = 5.0
fillet_radius = 2.0

tri_height = math.sqrt(3) / 2 * triangle_side
v1 = (0, 2 * tri_height / 3)
v2 = (-triangle_side / 2, -tri_height / 3)
v3 = (triangle_side / 2, -tri_height / 3)

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(triangle_side, 3)
    extrude(amount=plate_thickness)

solid_body = p.part

for vx, vy in [v1, v2, v3]:
    solid_body = solid_body - Pos(vx, vy, plate_thickness / 2) * Cylinder(vertex_hole_diameter / 2, plate_thickness)

solid_body = solid_body - Pos(0, 0, plate_thickness / 2) * Cylinder(central_hole_diameter / 2, plate_thickness)

with BuildPart() as rib_p:
    with BuildSketch() as rs:
        RegularPolygon(triangle_side + 2 * rib_offset, 3)
    extrude(amount=rib_height)

rib_solid = Pos(0, 0, plate_thickness) * rib_p.part

solid_body = solid_body + rib_solid

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "triangular_plate_with_rib"
export_step(part, "output.step")