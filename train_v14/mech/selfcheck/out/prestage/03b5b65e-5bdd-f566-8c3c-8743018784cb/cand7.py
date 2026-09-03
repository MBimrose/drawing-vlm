from build123d import *

plate_length = 100.0
plate_width = 70.0
plate_thickness = 8.0
rib_height = 6.0
rib_width = 10.0
rib_offset = 12.0
boss_diameter = 40.0
boss_height = 12.0
hole_diameter = 6.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 3
hole_cols = 4
chamfer_size = 1.0

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Pos(-plate_length/2 + rib_offset, 0, rib_height/2) * Box(rib_width, plate_width - 2*rib_offset, rib_height)
rib2 = Pos(plate_length/2 - rib_offset, 0, rib_height/2) * Box(rib_width, plate_width - 2*rib_offset, rib_height)
boss = Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)

solid_body = base + rib1 + rib2 + boss

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 30)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "plate_with_ribs_boss_and_holes"
export_step(part, "output.step")