from build123d import *
import math

plate_length = 80.0
plate_width = 80.0
plate_thickness = 8.0
boss_radius = 20.0
boss_height = 10.0
counterbore_diameter = 16.0
counterbore_depth = 4.0
through_hole_diameter = 4.0
mount_hole_diameter = 6.0
mount_hole_offset = 15.0
rib_width = 10.0
rib_height = 4.0
rib_offset = 5.0
chamfer_size = 2.0

result = Box(plate_length, plate_width, plate_thickness)
result = result + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)

top_z = plate_thickness/2 + boss_height
result = result - Pos(0, 0, top_z - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
result = result - Pos(0, 0, top_z - (boss_height + plate_thickness)/2) * Cylinder(through_hole_diameter/2, boss_height + plate_thickness)

mount_points = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

rib_positions = [
    (-plate_length/2 + rib_offset, -plate_width/2 + rib_offset),
    ( plate_length/2 - rib_offset, -plate_width/2 + rib_offset),
    ( plate_length/2 - rib_offset,  plate_width/2 - rib_offset),
    (-plate_length/2 + rib_offset,  plate_width/2 - rib_offset),
]
for x, y in rib_positions:
    result = result + Pos(x, y, rib_height/2) * Box(rib_width, rib_width, rib_height)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "plate_with_boss_and_ribs"
export_step(part, "output.step")