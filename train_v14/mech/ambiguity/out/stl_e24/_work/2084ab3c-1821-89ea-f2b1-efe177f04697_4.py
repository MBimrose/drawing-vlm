from build123d import *

plate_width = 80.0
plate_length = 60.0
plate_thickness = 3.0
fillet_radius = 1.5
hole_diameter = 3.2
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
slot_width = 12.0
slot_depth = 8.0
rib_height = 2.0
rib_thickness = 2.0
boss_diameter = 6.0
boss_height = 2.0

solid_body = Box(plate_width, plate_length, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

slot = Pos(0, plate_length / 2 - slot_depth / 2, plate_thickness / 2) * Box(slot_width, slot_depth, plate_thickness)
solid_body = solid_body - slot

rib = Pos(0, 0, plate_thickness) * Box(rib_thickness, plate_width - 10, rib_height)
solid_body = solid_body + rib

boss = Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "plate_with_rib_and_boss"
export_step(part, "output.step")