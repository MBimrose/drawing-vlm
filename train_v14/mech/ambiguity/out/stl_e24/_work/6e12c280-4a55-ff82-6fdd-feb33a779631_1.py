from build123d import *

bracket_length = 80.0
bracket_width = 50.0
bracket_thickness = 8.0
gusset_base = 20.0
gusset_height = 30.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.5
rib_thickness = 4.0
rib_height = 6.0
rib_spacing = 15.0
rib_offset_y = 10.0

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)

with BuildPart() as gp:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((bracket_length/2, -bracket_width/2), (bracket_length/2 + gusset_base, -bracket_width/2), (bracket_length/2, -bracket_width/2 + gusset_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)
gusset = gp.part

result = base + gusset

rib_cut = Box(rib_thickness, rib_height, bracket_thickness/2)
for y in [-rib_spacing/2, rib_spacing/2]:
    result = result - Pos(0, y, bracket_thickness/4) * rib_cut

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "bracket_with_gusset"
export_step(part, "output.step")