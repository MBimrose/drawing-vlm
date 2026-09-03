from build123d import *

cover_length = 80.0
cover_width = 60.0
cover_thickness = 12.0
wall_thickness = 2.0
boss_diameter = 20.0
boss_height = 8.0
fillet_radius = 1.5
chamfer_distance = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0

base = Pos(0, 0, cover_thickness/2) * Box(cover_length, cover_width, cover_thickness)
top_face = base.faces().sort_by(Axis.Z)[-1]
hollow = offset(base, amount=-wall_thickness, openings=[top_face])

boss = Pos(0, 0, cover_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
combined = hollow + boss

hole_r = mount_hole_diameter / 2
hole_h = cover_thickness + boss_height + 10
hole_z = cover_thickness + boss_height / 2
for x, y in [(cover_length/2 - mount_hole_offset, cover_width/2 - mount_hole_offset),
             (-cover_length/2 + mount_hole_offset, cover_width/2 - mount_hole_offset),
             (-cover_length/2 + mount_hole_offset, -cover_width/2 + mount_hole_offset),
             (cover_length/2 - mount_hole_offset, -cover_width/2 + mount_hole_offset)]:
    combined = combined - Pos(x, y, hole_z) * Cylinder(hole_r, hole_h)

combined = fillet(combined.edges().filter_by(Axis.Z), fillet_radius)
bottom_face = combined.faces().sort_by(Axis.Z)[0]
combined = chamfer(bottom_face.edges(), chamfer_distance)

part = combined
part.name = "cover_with_boss_and_holes"
export_step(part, "output.step")