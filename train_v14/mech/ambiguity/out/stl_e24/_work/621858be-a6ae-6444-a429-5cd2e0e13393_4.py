from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
height = 30.0
rib_height = 4.0
rib_thickness = 2.0
slot_width = 4.0
slot_depth = wall_thickness - 1.0
slot_count = 6
chamfer_size = 1.0
mount_hole_dia = 4.0
mount_hole_spacing = 30.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

result = Pos(0, 0, height/2) * Cylinder(outer_radius + wall_thickness, height)
result = result - Pos(0, 0, height/2) * Cylinder(outer_radius, height)

rib = Pos(0, 0, height - rib_height/2) * (Cylinder(outer_radius + wall_thickness + rib_thickness, rib_height) - Cylinder(outer_radius + wall_thickness, rib_height))
result = result + rib

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius + wall_thickness/2, 0, (height - 2*rib_height)/2) * Box(slot_width, slot_depth, height - 2*rib_height)
    result = result - slot

for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2), (mount_hole_spacing/2, -mount_hole_spacing/2), (mount_hole_spacing/2, mount_hole_spacing/2), (-mount_hole_spacing/2, mount_hole_spacing/2)]:
    result = result - Pos(x, y, height/2) * Cylinder(mount_hole_dia/2, height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "hollow_cylinder_with_ribs_and_slots"
export_step(part, "output.step")