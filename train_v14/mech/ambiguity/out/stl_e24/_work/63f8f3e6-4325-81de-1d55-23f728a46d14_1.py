from build123d import *

sheet_width = 80.0
sheet_depth = 60.0
sheet_thickness = 2.0
corner_radius = 15.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 2
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (sheet_width, 0))
            l2 = Line(l1 @ 1, (sheet_width, sheet_depth - corner_radius))
            arc = RadiusArc(l2 @ 1, (sheet_width - corner_radius, sheet_depth), corner_radius)
            l3 = Line(arc @ 1, (0, sheet_depth))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    extrude(amount=sheet_thickness)

solid_body = p.part

start_x = (sheet_width - (hole_cols - 1) * hole_spacing_x) / 2.0
start_y = (sheet_depth - (hole_rows - 1) * hole_spacing_y) / 2.0
for i in range(hole_cols):
    for j in range(hole_rows):
        px = start_x + i * hole_spacing_x
        py = start_y + j * hole_spacing_y
        solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter / 2, sheet_thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "sheet_with_holes_and_chamfer"
export_step(part, "output.step")