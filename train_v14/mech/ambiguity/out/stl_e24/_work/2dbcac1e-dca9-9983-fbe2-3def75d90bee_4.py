from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 3.0
rib_width = 15.0
hole_diameter = 6.5
hole_offset = 10.0
chamfer_distance = 1.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_distance)

rib = Pos(0, 0, plate_thickness + rib_height/2) * Box(rib_width, plate_width, rib_height)
solid_body = base + rib

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset)
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, (plate_thickness + rib_height)/2) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 2)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")