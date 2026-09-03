from build123d import *
import math

outer_diameter = 30.0
wall_thickness = 2.0
length = 80.0
groove_depth = 1.5
groove_angle = 60.0
groove_width = 2 * groove_depth * math.tan(math.radians(groove_angle / 2))
set_screw_diameter = 2.5
set_screw_offset = 20.0
chamfer_distance = 0.5
tab_width = 12.0
tab_height = 10.0
tab_thickness = 3.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=length)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness, openings=list(solid_body.faces()))

with BuildPart() as gp:
    with BuildSketch(Plane.YZ) as gs:
        with BuildLine() as gl:
            l1 = Line((0, 0), (groove_width / 2, -groove_depth))
            l2 = Line(l1 @ 1, (-groove_width / 2, -groove_depth))
            l3 = Line(l2 @ 1, (0, 0))
        make_face()
    extrude(amount=wall_thickness + 0.2)

groove = Pos(outer_diameter / 2 - wall_thickness / 2, 0, length / 2) * gp.part
solid_body = solid_body - groove

set_screw = Pos(outer_diameter / 2, 0, length / 2 + set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2, wall_thickness * 2)
solid_body = solid_body - set_screw

tab = Pos(outer_diameter / 2 - tab_thickness / 2, 0, length + tab_thickness / 2) * Box(tab_width, tab_thickness, tab_height)
solid_body = solid_body + tab

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

part = solid_body
part.name = "grooved_tube_with_tab"
export_step(part, "output.step")