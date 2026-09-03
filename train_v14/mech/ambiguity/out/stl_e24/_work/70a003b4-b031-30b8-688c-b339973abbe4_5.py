from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 10.0
chamfer_size = 1.0
slot_width = 4.0
slot_length = 12.0
slot_count = 4
mount_hole_diameter = 5.0
mount_hole_radius = 30.0
mount_hole_count = 4
pocket_diameter = 20.0
pocket_depth = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, thickness) - Cylinder(inner_radius, thickness)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

result = result - Pos(0, 0, thickness - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(inner_radius + slot_length/2, 0, thickness/2) * Box(slot_length, slot_width, thickness)
    result = result - slot

for i in range(mount_hole_count):
    angle = i * 360.0 / mount_hole_count
    px = mount_hole_radius * math.cos(math.radians(angle))
    py = mount_hole_radius * math.sin(math.radians(angle))
    result = result - Pos(px, py, 0) * Cylinder(mount_hole_diameter/2, thickness)

part = result
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")