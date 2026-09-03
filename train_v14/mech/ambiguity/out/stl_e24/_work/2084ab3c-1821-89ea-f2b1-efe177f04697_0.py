from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 3.0
edge_fillet_radius = 1.5
hole_diameter = 3.2
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
slot_width = 12.0
slot_length = 8.0
rib_thickness = 2.0
rib_height = 2.0
rib_length = 70.0
boss_diameter = 6.0
boss_height = 2.0

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), edge_fillet_radius)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

slot_y = plate_depth / 2 - slot_length / 2
solid_body = solid_body - Pos(0, slot_y, 0) * Box(slot_width, slot_length, plate_thickness * 2)

solid_body = solid_body + Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + Pos(0, 0, plate_thickness) * Box(rib_thickness, rib_length, rib_height)

part = solid_body
part.name = "plate_with_features"
export_step(part, "output.step")