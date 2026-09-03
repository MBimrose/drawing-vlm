from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 4.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 2.0
chamfer_size = 0.4
hole_diameter = 3.0
hole_offset = 5.0
rib_thickness = 2.0
rib_height = 2.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

pocket = Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset)
]
for x, y in hole_positions:
    base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

rib1 = Pos(0, plate_width/2 - rib_thickness/2, 0) * Box(plate_length - 2*hole_offset, rib_thickness, rib_height)
rib2 = Pos(0, -plate_width/2 + rib_thickness/2, 0) * Box(plate_length - 2*hole_offset, rib_thickness, rib_height)
rib3 = Pos(plate_length/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, plate_width - 2*hole_offset, rib_height)
rib4 = Pos(-plate_length/2 + rib_thickness/2, 0, 0) * Box(rib_thickness, plate_width - 2*hole_offset, rib_height)

part = base + rib1 + rib2 + rib3 + rib4
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")