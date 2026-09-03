from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
rib_height = 4.0
rib_width = 6.0
rib_length = bracket_length - 20.0
hole_diameter = 4.0
hole_spacing = 40.0
pocket_depth = 4.0
pocket_margin = 5.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 1)

rib = Pos(0, 0, bracket_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

pocket_w = bracket_length - 2 * pocket_margin
pocket_h = bracket_width - 2 * pocket_margin
pocket = Pos(0, 0, bracket_thickness/2 + rib_height - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)
solid_body = solid_body - pocket

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "bracket_with_rib_and_pocket"
export_step(part, "output.step")