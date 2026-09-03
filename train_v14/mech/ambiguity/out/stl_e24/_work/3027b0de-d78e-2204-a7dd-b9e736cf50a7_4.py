from build123d import *

plate_length = 100.0
plate_width = 50.0
plate_thickness = 10.0
pocket_length = 80.0
pocket_width = 30.0
pocket_depth = 5.0
chamfer_size = 0.5
hole_diameter = 3.0
hole_offset_x = 15.0
hole_offset_y = 10.0
rib_height = 5.0
rib_width = 5.0
rib_spacing = 20.0

result = Box(plate_length, plate_width, plate_thickness)

pocket = Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

hole_positions = [
    (-plate_length/2 + hole_offset_x, -plate_width/2 + hole_offset_y),
    ( plate_length/2 - hole_offset_x, -plate_width/2 + hole_offset_y),
    (-plate_length/2 + hole_offset_x,  plate_width/2 - hole_offset_y),
    ( plate_length/2 - hole_offset_x,  plate_width/2 - hole_offset_y),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

rib_count = int((plate_length - 2*hole_offset_x) // rib_spacing) + 1
for i in range(rib_count):
    x = -plate_length/2 + hole_offset_x + i * rib_spacing
    rib = Pos(x, 0, -plate_thickness/2 - rib_height/2) * Box(rib_width, rib_height, rib_height)
    result = result + rib

part = result
part.name = "plate_with_pocket_ribs"
export_step(part, "output.step")