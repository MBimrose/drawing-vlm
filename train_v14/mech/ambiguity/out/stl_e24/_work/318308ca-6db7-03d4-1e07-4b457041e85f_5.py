from build123d import *

length = 80.0
width = 30.0
thickness = 15.0
tab_width = 10.0
tab_length = 20.0
wall_thickness = 4.0
hole_diameter = 8.0
counterbore_diameter = 14.0
counterbore_depth = 5.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (width, 0), (width + tab_width, 0), (width + tab_width, tab_length),
                     (width, tab_length), (width, length), (0, length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

hole_x = width / 2
hole_y = length - tab_length / 2

solid_body = solid_body - Pos(hole_x, hole_y, thickness - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - Pos(hole_x, hole_y, thickness/2) * Cylinder(hole_diameter/2, thickness + 10)

chamfer_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
solid_body = chamfer(chamfer_edges, chamfer_size)

part = solid_body
part.name = "tabbed_shell_with_counterbore"
export_step(part, "output.step")