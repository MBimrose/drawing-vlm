from build123d import *

plate_length = 80.0
plate_width = 32.0
plate_thickness = 8.0
boss_radius = 8.0
boss_height = 24.0
hole_diameter = 6.0
hole_spacing = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        SlotOverall(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

boss1 = Pos(-plate_length/2 + boss_radius + 5, 0, plate_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
boss2 = Pos(plate_length/2 - boss_radius - 5, 0, -boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss1 + boss2

for x, y in [(0, 0), (-hole_spacing, 0), (hole_spacing, 0)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_bosses_and_holes"
export_step(part, "output.step")