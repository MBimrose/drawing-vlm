from build123d import *

outer_size = 80.0
wall_thickness = 5.0
height = 40.0
chamfer_size = 1.0
groove_width = 40.0
groove_depth = 8.0
groove_height = 10.0
hole_diameter = 3.0
hole_offset = 12.0

inner_size = outer_size - 2 * wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(outer_size, outer_size)
    extrude(amount=height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove = Pos(-outer_size/2 + groove_depth/2, 0, height/2) * Box(groove_depth, groove_height, groove_width)
solid_body = solid_body - groove

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

hole_positions = [
    (-outer_size/2 + hole_offset, 0),
    (outer_size/2 - hole_offset, 0),
    (0, -outer_size/2 + hole_offset),
    (0, outer_size/2 - hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, height) * Cylinder(hole_diameter/2, height)

part = solid_body
part.name = "shelled_box_with_groove_and_holes"
export_step(part, "output.step")