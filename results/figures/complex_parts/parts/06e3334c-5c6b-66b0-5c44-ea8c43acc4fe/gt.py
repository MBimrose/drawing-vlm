from build123d import *

base_radius = 50.0
thickness = 10.0
chamfer_size = 1.0
mount_hole_dia = 12.0
fillet_radius = 2.0
notch_width = 8.0
notch_depth = 5.0
rib_width = 6.0
rib_height = 20.0
rib_thickness = 2.0
rim_width = 5.0
rim_height = 3.0

import math

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(base_radius, 3)
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(mount_hole_dia/2, thickness * 2)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for i in range(3):
    notch = Rot(0, 0, i * 120) * Pos(0, 0, thickness/2) * Box(notch_width, notch_depth, thickness * 2)
    solid_body = solid_body - notch

with BuildPart() as rim_p:
    with BuildSketch() as rim_s:
        RegularPolygon(base_radius + rim_width, 3)
        RegularPolygon(base_radius, 3, mode=Mode.SUBTRACT)
    extrude(amount=rim_height)

rim = Pos(0, 0, thickness) * rim_p.part
rim = chamfer(rim.edges().filter_by(Axis.Z), chamfer_size)
solid_body = solid_body + rim

rib = Box(rib_width, rib_height, rib_thickness)
rib1 = Pos(base_radius/2, 0, thickness) * rib
rib2 = Rot(0, 0, 120) * Pos(-base_radius/4, base_radius*math.sqrt(3)/4, thickness) * rib
rib3 = Rot(0, 0, 240) * Pos(-base_radius/4, -base_radius*math.sqrt(3)/4, thickness) * rib
solid_body = solid_body + rib1 + rib2 + rib3

part = solid_body
part.name = "triangular_base_with_rim_and_ribs"
export_step(part, OUTPUT_PATH)