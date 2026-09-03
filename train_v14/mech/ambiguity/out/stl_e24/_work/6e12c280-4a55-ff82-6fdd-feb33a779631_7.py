from build123d import *

bracket_length = 80.0
bracket_width = 50.0
bracket_thickness = 8.0
gusset_height = 30.0
gusset_thickness = 6.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.5
rib_height = 4.0
rib_thickness = 3.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

with BuildPart() as g:
    with BuildSketch() as s:
        with BuildLine() as l:
            Polyline((bracket_length/2, -bracket_width/2),
                     (bracket_length/2 + gusset_height, -bracket_width/2),
                     (bracket_length/2, -bracket_width/2 + gusset_thickness),
                     close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part + g.part

rib = Pos(0, 0, rib_height/2) * Box(rib_thickness, bracket_width - 10, rib_height)
solid_body = solid_body + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "bracket_with_gusset_rib_holes"
export_step(part, "output.step")