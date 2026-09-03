from build123d import *

channel_width = 80.0
channel_height = 40.0
flange_thickness = 5.0
web_thickness = 5.0
length = 100.0
chamfer_size = 2.0
hole_diameter = 8.0
pattern_hole_diameter = 3.0
pattern_spacing = 12.0
pattern_rows = 3
pattern_cols = 4
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 3.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (channel_width, 0))
            l2 = Line(l1 @ 1, (channel_width, flange_thickness))
            l3 = Line(l2 @ 1, (web_thickness, flange_thickness))
            l4 = Line(l3 @ 1, (web_thickness, channel_height - flange_thickness))
            l5 = Line(l4 @ 1, (channel_width, channel_height - flange_thickness))
            l6 = Line(l5 @ 1, (channel_width, channel_height))
            l7 = Line(l6 @ 1, (0, channel_height))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    extrude(amount=length)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Pos(channel_width/2, length/2, channel_height/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, channel_width + 10)

for i in range(pattern_cols):
    for j in range(pattern_rows):
        y_off = (i - (pattern_cols - 1) / 2) * pattern_spacing
        z_off = (j - (pattern_rows - 1) / 2) * pattern_spacing
        solid_body = solid_body - Pos(web_thickness/2, length/2 + y_off, channel_height/2 + z_off) * Rot(0, 90, 0) * Cylinder(pattern_hole_diameter/2, web_thickness + 10)

solid_body = solid_body - Pos(pocket_depth/2, length/2, channel_height/2) * Box(pocket_depth, pocket_width, pocket_height)

part = solid_body
part.name = "C_channel_with_holes_and_pocket"
export_step(part, "output.step")