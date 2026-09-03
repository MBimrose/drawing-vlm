from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 4.0
pocket_chamfer = 2.0
hole_diameter = 5.0
hole_cbore_diameter = 6.0
hole_cbore_depth = 2.0
hole_spacing = 45.0
hole_offset_y = 20.0
rib_thickness = 3.0
rib_height = 4.0
rib_length = 60.0
rib_spacing = 30.0

base = Box(plate_length, plate_width, plate_thickness)

pocket = Box(pocket_length, pocket_width, pocket_depth)
pocket = chamfer(pocket.edges().filter_by(Axis.Z), pocket_chamfer)
pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * pocket
base = base - pocket

hole_positions = [(-hole_spacing/2, hole_offset_y), (hole_spacing/2, hole_offset_y), (0, -hole_offset_y)]
for x, y in hole_positions:
    base = base - Pos(x, y, plate_thickness/2 - hole_cbore_depth/2) * Cylinder(hole_cbore_diameter/2, hole_cbore_depth)
    base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib1 = Pos(0, rib_spacing/2, -plate_thickness/2 - rib_height/2) * Box(rib_length, rib_thickness, rib_height)
rib2 = Pos(0, -rib_spacing/2, -plate_thickness/2 - rib_height/2) * Box(rib_length, rib_thickness, rib_height)
base = base + rib1 + rib2

part = base
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")