from build123d import *
import math

side_length = 80.0
thickness = 10.0
central_hole_dia = 12.0
mount_hole_dia = 6.0
mount_hole_cbore_dia = 10.0
mount_hole_cbore_depth = 2.0
rib_offset = 5.0
rib_height = 3.0
chamfer_dist = 0.5

tri_height = math.sqrt(3) / 2 * side_length
v1 = (-side_length/2, -tri_height/3)
v2 = ( side_length/2, -tri_height/3)
v3 = (0, 2*tri_height/3)
vertices = [v1, v2, v3]

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(side_length, 3)
    extrude(amount=thickness)
solid = p.part

solid = solid - Pos(0, 0, thickness/2) * Cylinder(central_hole_dia/2, thickness)

for vx, vy in vertices:
    solid = solid - Pos(vx, vy, thickness - mount_hole_cbore_depth/2) * Cylinder(mount_hole_cbore_dia/2, mount_hole_cbore_depth)
    solid = solid - Pos(vx, vy, thickness/2) * Cylinder(mount_hole_dia/2, thickness)

with BuildPart() as rib_p:
    with BuildSketch() as rs:
        RegularPolygon(side_length - 2*rib_offset, 3)
    extrude(amount=rib_height)
rib_solid = Pos(0, 0, thickness) * rib_p.part

solid = solid + rib_solid
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_dist)

part = solid
part.name = "triangular_plate_with_rib"
export_step(part, "output.step")