from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
height = 40.0
relief_groove_diameter = 40.0
relief_groove_depth = 5.0
relief_groove_offset = 10.0
mount_hole_diameter = 5.0
mount_hole_count = 3
mount_hole_radius = (outer_diameter / 2) - 5.0
chamfer_size = 1.0
rib_thickness = 3.0
rib_height = height - 10.0
rib_count = 6
rib_angle = 360.0 / rib_count

result = Cylinder(outer_diameter / 2, height)
result = result - Cylinder(inner_diameter / 2, height)
result = result - Pos(0, 0, relief_groove_offset - relief_groove_depth / 2) * Cylinder(relief_groove_diameter / 2, relief_groove_depth)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    result = result - Pos(px, py, 0) * Cylinder(mount_hole_diameter / 2, height)

result = chamfer(result.edges(), chamfer_size)

for i in range(rib_count):
    angle = i * rib_angle
    rib = Rot(0, 0, angle) * Pos(outer_diameter / 2 - rib_thickness / 2, 0, 0) * Box(rib_thickness, rib_thickness, rib_height)
    result = result + rib

part = result
part.name = "flanged_disc_with_ribs"
export_step(part, "output.step")