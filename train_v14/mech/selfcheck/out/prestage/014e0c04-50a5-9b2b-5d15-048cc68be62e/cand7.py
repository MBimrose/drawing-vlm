from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 6.0
notch_width = 12.0
notch_depth = 4.0
notch_fillet_radius = 1.0
hole_diameter = 5.0
hole_offset_x = 25.0
rib_width = 6.0
rib_height = 3.0
rib_spacing = 20.0
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

notch = Pos(0, plate_width/2 - notch_depth/2, 0) * Box(notch_width, notch_depth, plate_thickness)
notch = fillet(notch.edges().filter_by(Axis.Z), notch_fillet_radius)
base = base - notch

for x, y in [(-hole_offset_x, 0), (hole_offset_x, 0)]:
    base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, plate_length - 2*rib_spacing, rib_height)
part = base + rib
part.name = "plate_with_notch_holes_and_rib"
export_step(part, "output.step")