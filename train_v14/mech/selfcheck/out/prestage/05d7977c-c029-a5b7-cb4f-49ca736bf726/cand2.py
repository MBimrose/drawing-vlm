from build123d import *

plate_width = 60.0
plate_depth = 40.0
plate_thickness = 8.0
boss_diameter = 20.0
boss_height = 12.0
hole_diameter = 6.0
hole_offset = 15.0
chamfer_size = 0.5
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_depth)
    extrude(amount=plate_thickness)
    with BuildSketch() as s2:
        Circle(boss_diameter / 2)
    extrude(amount=boss_height)

solid_body = p.part

hole_positions = [
    (hole_offset, hole_offset),
    (-hole_offset, hole_offset),
    (-hole_offset, -hole_offset),
    (hole_offset, -hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, 100)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")