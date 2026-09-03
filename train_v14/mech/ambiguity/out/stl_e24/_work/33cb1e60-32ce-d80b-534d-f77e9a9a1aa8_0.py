from build123d import *

rod_diameter = 30.0
rod_length = 80.0
groove_width = 6.0
groove_depth = 4.0
tab_width = 12.0
tab_height = 10.0
tab_thickness = 3.0
hole_diameter = 2.5
hole_offset_from_top = 20.0
hole_spacing = 40.0
chamfer_size = 0.5

solid_body = Cylinder(rod_diameter / 2, rod_length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
chamfer_edges = top_face.edges() + bottom_face.edges()
solid_body = chamfer(chamfer_edges, chamfer_size)

with BuildPart() as gp:
    with BuildSketch(Plane.YZ) as gs:
        with BuildLine() as gl:
            l1 = Line((0, 0), (groove_width / 2, groove_depth))
            l2 = Line(l1 @ 1, (-groove_width / 2, groove_depth))
            l3 = Line(l2 @ 1, (0, 0))
        make_face()
    extrude(amount=rod_length)
groove = Pos(rod_diameter / 2 - groove_depth, 0, 0) * gp.part
solid_body = solid_body - groove

tab = Pos(rod_diameter / 2 - tab_thickness / 2, 0, rod_length / 2) * Box(tab_width, tab_thickness, tab_height)
solid_body = solid_body + tab

for z_pos in [rod_length / 2 - hole_offset_from_top, rod_length / 2 - hole_offset_from_top - hole_spacing]:
    hole = Pos(rod_diameter / 2, 0, z_pos) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, rod_diameter)
    solid_body = solid_body - hole

part = solid_body
part.name = "grooved_rod_with_tab"
export_step(part, "output.step")