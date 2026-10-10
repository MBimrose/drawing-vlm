from build123d import *

base_length = 80.0
base_width = 80.0
base_thickness = 12.0
boss_diameter = 50.0
boss_height = 60.0
through_hole_diameter = 30.0
mount_hole_diameter = 8.0
mount_hole_offset = 10.0
chamfer_distance = 5.0
fillet_radius = 1.0
thread_clearance = 0.5

base = Box(base_length, base_width, base_thickness)
boss = Pos(0, 0, base_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

result = result - Cylinder(through_hole_diameter/2, 200)

mount_points = [
    (base_length/2 - mount_hole_offset, base_width/2 - mount_hole_offset),
    (-base_length/2 + mount_hole_offset, base_width/2 - mount_hole_offset),
    (-base_length/2 + mount_hole_offset, -base_width/2 + mount_hole_offset),
    (base_length/2 - mount_hole_offset, -base_width/2 + mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, 200)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance/2)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = fillet(bottom_face.edges(), fillet_radius)

part = result
part.name = "base_plate_with_boss"
export_step(part, "output.step")