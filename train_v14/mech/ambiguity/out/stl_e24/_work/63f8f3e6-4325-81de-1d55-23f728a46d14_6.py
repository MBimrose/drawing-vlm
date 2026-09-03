from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 2.0
corner_radius = 15.0
chamfer_size = 0.5
hole_diameter = 4.0
hole_offset = 10.0
hole_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (plate_length, 0))
            l2 = Line(l1 @ 1, (plate_length, plate_width - corner_radius))
            arc = RadiusArc(l2 @ 1, (plate_length - corner_radius, plate_width), corner_radius)
            l3 = Line(arc @ 1, (0, plate_width))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

hole_positions = [
    (hole_offset, hole_offset),
    (plate_length - hole_offset, hole_offset),
    (hole_offset, plate_width - hole_offset),
    (plate_length - hole_offset, plate_width - hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

part = solid_body
part.name = "plate_with_holes"
export_step(part, "output.step")