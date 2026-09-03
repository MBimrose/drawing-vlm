from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 20.0
rib_height = 5.0
rib_width = 6.0
rib_count = 12
set_screw_diameter = 2.0
set_screw_offset = 22.0
keyway_width = 4.0
keyway_depth = 6.0
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, thickness) - Cylinder(inner_radius, thickness)

rib = Pos(outer_radius + rib_height / 2.0, 0, thickness / 2.0) * Box(rib_height, rib_width, thickness)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

result = result + ribs

result = result - Pos(set_screw_offset, 0, 0) * Cylinder(set_screw_diameter / 2, thickness * 2)

keyway = Pos(inner_radius - keyway_depth / 2.0, 0, 0) * Box(keyway_depth, keyway_width, thickness)
result = result - keyway

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "pulley_with_ribs"
export_step(part, "output.step")