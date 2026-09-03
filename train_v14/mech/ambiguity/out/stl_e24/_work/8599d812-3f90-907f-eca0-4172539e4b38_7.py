from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 4.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 2.0
hole_diameter = 3.0
hole_offset = 5.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

# Pocket cut from top face
pocket = Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 - pocket_depth/2) * pocket

# Four through holes at corners
hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

# Chamfer all vertical edges
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_pocket_and_holes"
export_step(part, "output.step")