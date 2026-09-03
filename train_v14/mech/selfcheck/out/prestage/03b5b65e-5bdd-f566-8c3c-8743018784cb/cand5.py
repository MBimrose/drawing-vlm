from build123d import *

plate_length = 100.0
plate_width = 70.0
plate_thickness = 8.0
boss_diameter = 40.0
boss_height = 6.0
hole_diameter = 6.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 3
hole_cols = 4
rib_width = 8.0
rib_height = 3.0
rib_offset = 30.0
fillet_radius = 0.5

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness) * Cylinder(boss_diameter/2, boss_height)
rib1 = Pos(-rib_offset, 0, plate_thickness + rib_height/2) * Box(rib_width, plate_width - 10, rib_height)
rib2 = Pos(rib_offset, 0, plate_thickness + rib_height/2) * Box(rib_width, plate_width - 10, rib_height)

solid_body = base + boss + rib1 + rib2

hole_h = plate_thickness + boss_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness) * Cylinder(hole_diameter/2, hole_h)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "plate_with_boss_ribs_and_holes"
export_step(part, "output.step")