from build123d import *

plate_length = 80.0
plate_width = 80.0
plate_thickness = 5.0
boss_height = 25.0
hex_radius = 30.0
circle_radius = 20.0
chamfer_distance = 2.0
hole_diameter = 5.0
hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
    with BuildSketch() as s2:
        RegularPolygon(hex_radius, 6)
    with BuildSketch(Plane.XY.offset(boss_height)) as s3:
        Circle(circle_radius)
    loft()

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

part = solid_body
part.name = "plate_with_lofted_boss"
export_step(part, "output.step")