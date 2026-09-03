from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 10.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 4
fillet_radius = 1.5
rib_height = 2.0
rib_width = 5.0
rib_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

rib = Pos(0, -plate_width/2 + rib_offset + rib_width/2, -rib_height/2) * Box(plate_length - 2*rib_offset, rib_width, rib_height)
solid_body = solid_body + rib

start_x = -((hole_cols - 1) * hole_spacing_x) / 2
start_y = -((hole_rows - 1) * hole_spacing_y) / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = start_x + i * hole_spacing_x
        y = start_y + j * hole_spacing_y
        hole = Pos(x, y, plate_thickness + boss_height/2) * Cylinder(hole_diameter/2, plate_thickness + boss_height + 10)
        solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_boss_rib_and_holes"
export_step(part, "output.step")