from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 5.0
rib_height = 2.0
boss_diameter = 15.0
boss_height = 4.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 15.0
hole_rows = 3
hole_cols = 4
fillet_radius = 0.8

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Pos(0, 0, plate_thickness) * Box(plate_length - 2 * rib_width, rib_width, rib_height)
rib2 = Pos(0, 0, plate_thickness) * Box(rib_width, plate_width - 2 * rib_width, rib_height)
boss = Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)

combined = base + rib1 + rib2 + boss

top_face = combined.faces().sort_by(Axis.Z)[-1]
combined = fillet(top_face.edges(), fillet_radius)

hole_depth = plate_thickness + boss_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        combined = combined - Pos(x, y, 0) * Cylinder(hole_diameter / 2, hole_depth)

part = combined
part.name = "plate_with_ribs_boss_and_holes"
export_step(part, "output.step")