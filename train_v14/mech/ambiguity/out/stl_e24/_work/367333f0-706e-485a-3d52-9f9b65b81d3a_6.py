from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_size = 40.0
hole_diameter = 6.0
countersink_diameter = 10.0
countersink_angle = 82.0
edge_offset = 10.0
rib_width = 4.0
rib_length = 20.0
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges(), chamfer_size)

pocket = Box(pocket_size, pocket_size, plate_thickness)
base = base - pocket

hole_positions = [
    (-plate_length/2 + edge_offset, -plate_width/2 + edge_offset),
    ( plate_length/2 - edge_offset, -plate_width/2 + edge_offset),
    (-plate_length/2 + edge_offset,  plate_width/2 - edge_offset),
    ( plate_length/2 - edge_offset,  plate_width/2 - edge_offset)
]

for x, y in hole_positions:
    base = base - Pos(x, y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)

rib1 = Pos(0, plate_width/2 - rib_width/2 - edge_offset/2, 0) * Box(rib_length, rib_width, plate_thickness)
rib2 = Pos(0, -plate_width/2 + rib_width/2 + edge_offset/2, 0) * Box(rib_length, rib_width, plate_thickness)

part = base + rib1 + rib2
part.name = "plate_with_pocket_ribs"
export_step(part, "output.step")