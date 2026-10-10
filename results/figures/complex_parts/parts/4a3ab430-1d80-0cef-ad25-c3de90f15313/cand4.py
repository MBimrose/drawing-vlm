from build123d import *

base_length = 80.0
base_width = 80.0
base_thickness = 5.0
hex_radius = 30.0
loft_height = 20.0
top_circle_radius = 20.0
chamfer_distance = 2.0
hole_diameter = 5.0
hole_offset = 10.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)

with BuildPart() as p:
    with BuildSketch(Plane.XY.offset(base_thickness)) as s1:
        RegularPolygon(hex_radius, 6)
    with BuildSketch(Plane.XY.offset(base_thickness + loft_height)) as s2:
        Circle(top_circle_radius)
    loft()
loft_body = p.part

result = base + loft_body

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

hole_positions = [
    (base_length/2 - hole_offset, base_width/2 - hole_offset),
    (-base_length/2 + hole_offset, base_width/2 - hole_offset),
    (-base_length/2 + hole_offset, -base_width/2 + hole_offset),
    (base_length/2 - hole_offset, -base_width/2 + hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

part = result
part.name = "base_with_loft_and_holes"
export_step(part, "output.step")