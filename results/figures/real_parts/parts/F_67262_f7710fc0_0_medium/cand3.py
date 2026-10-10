from build123d import *

plate_length = 80.0
plate_width = 32.0
plate_thickness = 8.0
hole_diameter = 12.0
fillet_radius = 16.0
mount_hole_diameter = 6.0
mount_hole_spacing = 40.0
boss_radius = 8.0
boss_height = 24.0
boss_offset = 12.0

with BuildPart() as p:
    with BuildSketch() as s:
        SlotOverall(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 2)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 2)

solid_body = solid_body + Pos(-plate_length/2 + boss_offset, 0, plate_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + Pos(plate_length/2 - boss_offset, 0, -boss_height/2) * Cylinder(boss_radius, boss_height)

part = solid_body
part.name = "plate_with_bosses"
export_step(part, "output.step")