from build123d import *
import math

plate_width = 80.0
plate_height = 80.0
plate_thickness = 8.0
boss_radius = 20.0
boss_height = 12.0
counterbore_radius = 8.0
counterbore_depth = 6.0
through_hole_radius = 2.0
mount_hole_radius = 3.0
mount_hole_distance = 30.0
chamfer_size = 1.5
rib_width = 10.0
rib_height = 4.0
rib_offset = 5.0
notch_width = 10.0
notch_depth = 5.0

result = Box(plate_width, plate_height, plate_thickness)

notch_positions = [
    (-plate_width/2 + notch_width/2, -plate_height/2 + notch_depth/2),
    (plate_width/2 - notch_width/2, -plate_height/2 + notch_depth/2),
    (-plate_width/2 + notch_width/2, plate_height/2 - notch_depth/2),
    (plate_width/2 - notch_width/2, plate_height/2 - notch_depth/2),
]
for x, y in notch_positions:
    result = result - Pos(x, y, 0) * Box(notch_width, notch_depth, plate_thickness)

rib_positions = [
    (-plate_width/2 + rib_offset + rib_width/2, 0),
    (plate_width/2 - rib_offset - rib_width/2, 0),
    (0, -plate_height/2 + rib_offset + rib_width/2),
    (0, plate_height/2 - rib_offset - rib_width/2),
]
for x, y in rib_positions:
    result = result + Pos(x, y, 0) * Box(rib_width, rib_height, plate_thickness)

result = result + Pos(0, 0, plate_thickness) * Cylinder(boss_radius, boss_height)

result = result - Pos(0, 0, plate_thickness + boss_height - counterbore_depth/2) * Cylinder(counterbore_radius, counterbore_depth)

result = result - Pos(0, 0, (plate_thickness + boss_height)/2) * Cylinder(through_hole_radius, plate_thickness + boss_height)

mount_positions = [
    (mount_hole_distance, mount_hole_distance),
    (-mount_hole_distance, mount_hole_distance),
    (mount_hole_distance, -mount_hole_distance),
    (-mount_hole_distance, -mount_hole_distance),
]
for x, y in mount_positions:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_radius, plate_thickness)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "plate_with_boss_and_ribs"
export_step(part, "output.step")