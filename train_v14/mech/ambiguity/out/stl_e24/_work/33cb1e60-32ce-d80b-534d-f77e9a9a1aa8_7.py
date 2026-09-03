from build123d import *

body_diameter = 30.0
body_length = 80.0
wall_thickness = 2.0
dovetail_width = 8.0
dovetail_depth = 6.0
set_screw_diameter = 2.5
set_screw_offset = 20.0
snap_tab_length = 12.0
snap_tab_thickness = 3.0
snap_tab_height = 10.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(body_diameter / 2)
    extrude(amount=body_length)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

with BuildPart() as dovetail_p:
    with BuildSketch(Plane.YZ) as ds:
        with BuildLine() as dl:
            Polyline((0, 0), (dovetail_width, 0), (0, dovetail_depth), close=True)
        make_face()
    extrude(amount=wall_thickness)

dovetail_cut = Pos(body_diameter / 2 - wall_thickness, 0, body_length / 2) * dovetail_p.part
solid_body = solid_body - dovetail_cut

set_screw_hole = Pos(body_diameter / 2 - wall_thickness / 2, 0, body_length / 2 + set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2, wall_thickness * 2)
solid_body = solid_body - set_screw_hole

snap_tab = Pos(body_diameter / 2 - snap_tab_thickness / 2, 0, body_length) * Box(snap_tab_length, snap_tab_thickness, snap_tab_height)
solid_body = solid_body + snap_tab

part = solid_body
part.name = "dovetail_shaft"
export_step(part, "output.step")