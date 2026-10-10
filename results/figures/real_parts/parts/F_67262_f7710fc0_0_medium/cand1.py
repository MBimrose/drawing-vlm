from build123d import *

plate_length = 80.0
plate_width = 32.0
plate_thickness = 8.0
boss_radius = 8.0
boss_height = 24.0
boss_offset = 12.0
central_hole_diameter = 10.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        SlotOverall(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

boss1 = Pos(-plate_length/2 + boss_offset, 0, plate_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
boss2 = Pos(plate_length/2 - boss_offset, 0, -boss_height/2) * Cylinder(boss_radius, boss_height)

solid_body = solid_body + boss1 + boss2

solid_body = solid_body - Cylinder(central_hole_diameter/2, 100)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, 100)

solid_body = chamfer(solid_body.edges(), chamfer_distance)

part = solid_body
part.name = "plate_with_bosses_and_holes"
export_step(part, "output.step")