from build123d import *

shaft_radius = 5.0
collar_outer_radius = 15.0
collar_length = 30.0
tap_hole_diameter = 6.8
vent_hole_diameter = 4.0
rib_height = 2.0
rib_width = 4.0
rib_axial_length = collar_length * 0.8
rib_count = 12
chamfer_distance = 0.5

import math

outer = Cylinder(collar_outer_radius, collar_length)
inner = Cylinder(shaft_radius, collar_length + 2)
result = outer - inner

result = result - Cylinder(tap_hole_diameter / 2, collar_length)

result = result - Pos(collar_outer_radius, 0, collar_length / 2) * Rot(90, 0, 0) * Cylinder(vent_hole_diameter / 2, collar_outer_radius * 2)
result = result - Pos(-collar_outer_radius, 0, collar_length / 2) * Rot(90, 0, 0) * Cylinder(vent_hole_diameter / 2, collar_outer_radius * 2)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Box(rib_height, rib_width, rib_axial_length)
    px = (collar_outer_radius - rib_height / 2) * math.cos(math.radians(angle))
    py = (collar_outer_radius - rib_height / 2) * math.sin(math.radians(angle))
    result = result + Pos(px, py, collar_length / 2) * Rot(0, 0, angle) * rib

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "collar_with_ribs"
export_step(part, OUTPUT_PATH)