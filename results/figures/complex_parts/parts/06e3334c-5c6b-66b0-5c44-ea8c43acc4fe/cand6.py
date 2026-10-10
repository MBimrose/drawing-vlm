from build123d import *
import math

side_length = 80.0
base_thickness = 10.0
rib_height = 3.0
rib_offset = 5.0
central_hole_diameter = 12.0
vertex_hole_diameter = 5.0
chamfer_distance = 2.0

tri_height = math.sqrt(3) / 2 * side_length
v0 = (-side_length/2, -tri_height/3)
v1 = ( side_length/2, -tri_height/3)
v2 = (0.0, 2*tri_height/3)
vertices = [v0, v1, v2]

with BuildPart() as p:
    with BuildSketch() as s1:
        RegularPolygon(side_length, 3)
    extrude(amount=base_thickness)
    with BuildSketch(Plane.XY.offset(base_thickness)) as s2:
        RegularPolygon(side_length + 2*rib_offset, 3)
    extrude(amount=rib_height)

solid_body = p.part
total_height = base_thickness + rib_height

solid_body = solid_body - Pos(0, 0, total_height/2) * Cylinder(central_hole_diameter/2, total_height)

for vx, vy in vertices:
    solid_body = solid_body - Pos(vx, vy, total_height/2) * Cylinder(vertex_hole_diameter/2, total_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "triangular_plate_with_rib"
export_step(part, "output.step")