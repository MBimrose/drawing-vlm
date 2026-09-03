from build123d import *

panel_width = 80.0
panel_height = 60.0
panel_thickness = 2.0
corner_radius = 15.0
hole_diameter = 4.0
hole_offset = 10.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-panel_width/2, -panel_height/2), (panel_width/2, -panel_height/2))
            l2 = Line(l1@1, (panel_width/2, panel_height/2 - corner_radius))
            arc = RadiusArc(l2@1, (panel_width/2 - corner_radius, panel_height/2), corner_radius)
            l3 = Line(arc@1, (-panel_width/2, panel_height/2))
            l4 = Line(l3@1, (-panel_width/2, -panel_height/2))
        make_face()
    extrude(amount=panel_thickness)

solid_body = p.part

hole_positions = [
    (hole_offset, hole_offset),
    (panel_width - hole_offset, hole_offset),
    (hole_offset, panel_height - hole_offset),
    (panel_width - hole_offset, panel_height - hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, panel_thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "panel_with_corner_cutout"
export_step(part, "output.step")