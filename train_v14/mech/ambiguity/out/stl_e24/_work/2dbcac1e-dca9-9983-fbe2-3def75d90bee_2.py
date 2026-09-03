from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 15.0
rib_height = 3.0
hole_diameter = 6.5
hole_offset = 10.0
pocket_length = 20.0
pocket_width = 30.0
pocket_depth = 2.0
chamfer_size = 1.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width, rib_height)
result = base + rib

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

pocket = Pos(0, 0, plate_thickness/2 + rib_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

part = result
part.name = "plate_with_rib_holes_pocket"
export_step(part, "output.step")