from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 2.0
corner_radius = 15.0
hole_diameter = 4.0
hole_offset = 10.0
chamfer_size = 0.5
tab_width = 20.0
tab_height = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (plate_width, 0))
            l2 = Line(l1 @ 1, (plate_width, plate_height - corner_radius))
            a1 = RadiusArc(l2 @ 1, (plate_width - corner_radius, plate_height), corner_radius)
            l3 = Line(a1 @ 1, (0, plate_height))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part

tab = Pos(-tab_width / 2, plate_height / 2, plate_thickness / 2) * Box(tab_width, tab_height, plate_thickness)
solid_body = solid_body + tab

hole_positions = [
    (hole_offset, hole_offset),
    (plate_width - hole_offset, hole_offset),
    (hole_offset, plate_height - hole_offset),
    (plate_width - hole_offset, plate_height - hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness / 2) * Cylinder(hole_diameter / 2, plate_thickness * 2)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_tab_and_holes"
export_step(part, "output.step")