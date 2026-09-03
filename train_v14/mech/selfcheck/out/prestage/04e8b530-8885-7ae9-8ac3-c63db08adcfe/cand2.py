from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
cap_height = 30.0
inner_diameter = outer_diameter - 2 * wall_thickness
groove_depth = 2.0
groove_width = 2.0
groove_position = 10.0
chamfer_size = 2.0
fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 30.0
rib_thickness = 2.0
rib_width = 3.0
rib_height = 20.0
rib_count = 8

result = Cylinder(outer_diameter / 2, cap_height)
result = result - Cylinder(inner_diameter / 2, cap_height)

groove_radius = (inner_diameter / 2) - groove_depth
result = result - Pos(0, 0, cap_height - groove_position - groove_width / 2) * Cylinder(groove_radius, groove_width)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = fillet(bottom_face.edges(), fillet_radius)

for i in range(4):
    angle = math.radians(i * 90)
    px = mount_hole_offset * math.cos(angle)
    py = mount_hole_offset * math.sin(angle)
    result = result - Pos(px, py, cap_height / 2) * Cylinder(mount_hole_diameter / 2, cap_height)

for i in range(rib_count):
    angle = math.radians(i * 360 / rib_count)
    px = (inner_diameter / 2) * math.cos(angle)
    py = (inner_diameter / 2) * math.sin(angle)
    result = result + Pos(px, py, cap_height / 2) * Rot(0, 0, math.degrees(angle)) * Box(rib_thickness, rib_width, rib_height)

part = result
part.name = "cap_with_groove_and_ribs"
export_step(part, "output.step")