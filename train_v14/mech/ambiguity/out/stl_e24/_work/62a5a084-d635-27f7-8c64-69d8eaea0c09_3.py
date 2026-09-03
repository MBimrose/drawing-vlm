from build123d import *
import math

outer_diameter = 30.0
inner_diameter = 12.0
collar_length = 20.0
rib_thickness = 2.0
rib_height = 8.0
rib_count = 3
set_screw_diameter = 6.0
set_screw_head_diameter = 10.0
set_screw_head_depth = 4.0
set_screw_offset = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=collar_length)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, collar_length / 2) * Cylinder(inner_radius, collar_length)

rib = Pos(outer_radius + rib_thickness / 2.0, collar_length / 2.0, rib_height / 2.0) * Box(rib_thickness, collar_length, rib_height)
ribs = rib
for i in range(1, rib_count):
    angle = 360.0 / rib_count * i
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

cbore = Pos(outer_radius - set_screw_head_depth / 2.0, 0, collar_length / 2.0 + set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_head_diameter / 2.0, set_screw_head_depth)
shaft = Pos(outer_radius - wall_thickness / 2.0, 0, collar_length / 2.0 + set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, wall_thickness)

solid_body = solid_body - cbore - shaft

part = solid_body
part.name = "collar_with_ribs"
export_step(part, "output.step")