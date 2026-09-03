from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 12.0
pocket_diameter = 30.0
pocket_depth = 6.0
rib_width = 15.0
rib_height = 6.0
hole_diameter = 5.0
countersink_diameter = 10.0
countersink_angle = 82.0
hole_offset = 15.0
chamfer_size = 1.0

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Pos(0, plate_width/2 - rib_width/2, 0) * Box(plate_length, rib_width, rib_height)
rib2 = Pos(0, -plate_width/2 + rib_width/2, 0) * Box(plate_length, rib_width, rib_height)
rib3 = Pos(plate_length/2 - rib_width/2, 0, 0) * Box(rib_width, plate_width, rib_height)
rib4 = Pos(-plate_length/2 + rib_width/2, 0, 0) * Box(rib_width, plate_width, rib_height)

solid_body = base + rib1 + rib2 + rib3 + rib4

solid_body = solid_body - Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_ribs_pocket_holes"
export_step(part, "output.step")