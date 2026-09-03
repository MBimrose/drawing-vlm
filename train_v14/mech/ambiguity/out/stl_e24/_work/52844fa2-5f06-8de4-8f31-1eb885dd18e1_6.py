from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
cutout_width = 40.0
cutout_height = 30.0
cutout_fillet_radius = 2.0
hole_diameter = 5.0
hole_cbore_diameter = 6.0
hole_cbore_depth = 2.0
hole_offset = 15.0
rib_thickness = 3.0
rib_height = 4.0
rib_offset = 10.0

base = Box(plate_width, plate_height, plate_thickness)

cutout = Box(cutout_width, cutout_height, plate_thickness + 1)
cutout = fillet(cutout.edges().filter_by(Axis.Z), cutout_fillet_radius)

result = base - cutout

hole_positions = [
    (-plate_width/2 + hole_offset, plate_height/2 - hole_offset),
    (plate_width/2 - hole_offset, plate_height/2 - hole_offset),
    (0, -plate_height/2 + hole_offset)
]

for x, y in hole_positions:
    result = result - Pos(x, y, plate_thickness/2 - hole_cbore_depth/2) * Cylinder(hole_cbore_diameter/2, hole_cbore_depth)
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

rib1 = Pos(0, plate_height/2 - rib_offset - rib_thickness/2, -plate_thickness/2 - rib_height/2) * Box(plate_width - 2*rib_offset, rib_thickness, rib_height)
rib2 = Pos(0, -plate_height/2 + rib_offset + rib_thickness/2, -plate_thickness/2 - rib_height/2) * Box(plate_width - 2*rib_offset, rib_thickness, rib_height)

result = result + rib1 + rib2

part = result
part.name = "plate_with_cutout_holes_and_ribs"
export_step(part, "output.step")