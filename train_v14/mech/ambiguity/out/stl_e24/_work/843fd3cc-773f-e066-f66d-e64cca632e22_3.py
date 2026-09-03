from build123d import *
import math

outer_radius = 45.0
inner_radius = 15.0
thickness = 5.0
rib_height = 2.0
rib_inner_radius = inner_radius
rib_outer_radius = 22.5
central_hole_diameter = 9.0
mount_hole_diameter = 5.0
mount_hole_radius = 30.0
mount_hole_angle = 120.0
slot_width = 6.0
slot_length = 20.0
slot_offset = 35.0
chamfer_distance = 0.6

base = Pos(0, 0, thickness/2) * Cylinder(outer_radius, thickness)
rib = Pos(0, 0, thickness/2) * (Cylinder(rib_outer_radius, thickness) - Cylinder(rib_inner_radius, thickness))
result = base + rib

result = result - Pos(0, 0, thickness/2) * Cylinder(central_hole_diameter/2, thickness)

for i in range(2):
    angle = math.radians(i * mount_hole_angle)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    result = result - Pos(px, py, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)

result = result - Pos(slot_offset, 0, thickness/2) * Box(slot_width, slot_length, thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "flanged_disc_with_rib"
export_step(part, "output.step")