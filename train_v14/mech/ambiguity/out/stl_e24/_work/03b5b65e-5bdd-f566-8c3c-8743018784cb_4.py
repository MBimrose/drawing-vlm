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
rib_height = 4.0
rib_offset = 10.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness) * Cylinder(boss_diameter/2, boss_height)
rib1 = Pos(-plate_length/2 + rib_offset + rib_width/2, 0, plate_thickness) * Box(rib_width, plate_width - 2*rib_offset, rib_height)
rib2 = Pos(plate_length/2 - rib_offset - rib_width/2, 0, plate_thickness) * Box(rib_width, plate_width - 2*rib_offset, rib_height)

solid = base + boss + rib1 + rib2

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid = solid - Pos(x, y, plate_thickness) * Cylinder(hole_diameter/2, 100)

part = solid
part.name = "plate_with_boss_ribs_and_holes"
export_step(part, "output.step")