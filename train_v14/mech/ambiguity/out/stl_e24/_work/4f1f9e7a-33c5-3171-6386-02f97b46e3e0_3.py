from build123d import *

base_width = 50.0
base_length = 70.0
body_height = 50.0
top_width = 45.0
top_length = 65.0
tab_width = 20.0
tab_height = 30.0
tab_thickness = 5.0
hole_diameter = 8.0
chamfer_size = 1.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 5.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Rectangle(base_width, base_length)
    with BuildSketch(Plane.XY.offset(body_height)) as s2:
        Rectangle(top_width, top_length)
    loft()

solid_body = p.part

tab = Pos(base_width/2 + tab_thickness/2, 0, body_height/2) * Box(tab_thickness, tab_width, tab_height)
solid_body = solid_body + tab

solid_body = solid_body - Cylinder(hole_diameter/2, body_height + 1)

pocket = Pos(0, 0, body_height - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "lofted_body_with_tab"
export_step(part, "output.step")