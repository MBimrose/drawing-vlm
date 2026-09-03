from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 3.0
edge_fillet_radius = 1.5
notch_width = 10.0
notch_depth = 8.0
rib_width = 2.0
rib_height = 2.0
rib_offset = 10.0
boss_diameter = 6.0
boss_height = 2.0
hole_diameter = 3.2
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3

base = Box(plate_width, plate_depth, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), edge_fillet_radius)

notch = Pos(0, plate_depth/2 - notch_depth/2, plate_thickness/2) * Box(notch_width, notch_depth, plate_thickness)
base = base - notch

rib = Pos(0, -plate_depth/2 + rib_offset, plate_thickness) * Box(rib_width, plate_depth, rib_height)
base = base + rib

boss = Pos(0, 0, plate_thickness) * Cylinder(boss_diameter/2, boss_height)
base = base + boss

hole_depth = plate_thickness + rib_height + boss_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        base = base - Pos(x, y, plate_thickness) * Cylinder(hole_diameter/2, hole_depth)

part = base
part.name = "plate_with_rib_boss_holes"
export_step(part, "output.step")