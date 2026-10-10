from build123d import *

plate_width = 80.0
plate_height = 80.0
plate_thickness = 15.0
boss_radius = 20.0
boss_height = 60.0
wall_thickness = 5.0
chamfer_size = 5.0
fillet_radius = 2.0
mount_hole_dia = 8.0
mount_hole_offset = 10.0

base = Box(plate_width, plate_height, plate_thickness)
boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius + wall_thickness, boss_height)
solid_body = base + boss

solid_body = solid_body - Cylinder(boss_radius, 200)

hole_positions = [
    (plate_width/2 - mount_hole_offset, plate_height/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, plate_height/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, -plate_height/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, -plate_height/2 + mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, 200)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size * 0.25)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

part = solid_body
part.name = "plate_with_boss"
export_step(part, "output.step")