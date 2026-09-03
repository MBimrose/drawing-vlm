from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
rim_height = 4.0
rim_thickness = 4.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
fillet_radius = 2.0
rib_width = 6.0
rib_height = 2.0
rib_offset = 5.0

base = Box(plate_length, plate_width, plate_thickness)
rim_outer = Pos(0, 0, plate_thickness) * Box(plate_length, plate_width, rim_height)
rim_inner = Pos(0, 0, plate_thickness) * Box(plate_length - 2*rim_thickness, plate_width - 2*rim_thickness, rim_height)
rim = rim_outer - rim_inner
result = base + rim

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

rib1 = Pos(-plate_length/2 + rib_offset, 0, -rib_height/2) * Box(rib_width, plate_width - 2*rib_offset, rib_height)
rib2 = Pos(plate_length/2 - rib_offset, 0, -rib_height/2) * Box(rib_width, plate_width - 2*rib_offset, rib_height)
result = result + rib1 + rib2

hole_depth = plate_thickness + rim_height + rib_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, hole_depth)

part = result
part.name = "plate_with_rim_ribs_and_holes"
export_step(part, "output.step")