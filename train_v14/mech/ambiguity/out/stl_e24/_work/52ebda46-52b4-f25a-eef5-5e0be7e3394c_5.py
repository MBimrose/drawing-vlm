from build123d import *

inner_diameter = 20.0
outer_diameter = 40.0
collar_length = 30.0
rib_height = 5.0
rib_width = 10.0
set_screw_diameter = 4.0
set_screw_head_diameter = 7.0
set_screw_head_depth = 3.0
set_screw_offset = 12.0
chamfer_size = 0.8

inner_radius = inner_diameter / 2.0
outer_radius = outer_diameter / 2.0
rib_outer_radius = outer_radius + rib_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline(
                (inner_radius, 0),
                (inner_radius, collar_length - rib_width),
                (outer_radius, collar_length - rib_width),
                (outer_radius, collar_length),
                (rib_outer_radius, collar_length),
                (rib_outer_radius, 0),
                (inner_radius, 0),
                close=True
            )
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

import math
for i in range(4):
    angle = math.radians(i * 90)
    px = set_screw_offset * math.cos(angle)
    py = set_screw_offset * math.sin(angle)
    shaft = Pos(px, py, set_screw_offset) * Rot(0, 90, i * 90) * Cylinder(set_screw_diameter / 2, 2 * rib_outer_radius)
    cbore = Pos(px, py, set_screw_offset) * Rot(0, 90, i * 90) * Cylinder(set_screw_head_diameter / 2, set_screw_head_depth)
    solid_body = solid_body - shaft - cbore

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "collar_with_rib_and_set_screws"
export_step(part, "output.step")