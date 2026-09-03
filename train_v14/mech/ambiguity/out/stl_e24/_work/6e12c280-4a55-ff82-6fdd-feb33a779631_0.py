from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
gusset_length = 20.0
gusset_width = 15.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.5
rib_thickness = 3.0
rib_height = 4.0

base_plate = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as g:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((0, 0), (gusset_length, 0), (0, gusset_width), close=True)
        make_face()
    extrude(amount=plate_thickness)
gusset = Pos(plate_length / 2, -plate_width / 2, -plate_thickness / 2) * g.part

bracket = base_plate + gusset

rib = Pos(0, 0, -plate_thickness / 2 + rib_height / 2) * Box(rib_thickness, plate_width - 2 * gusset_width, rib_height)
bracket = bracket + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        bracket = bracket - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

bracket = chamfer(bracket.edges().filter_by(Axis.Z), chamfer_size)

part = bracket
part.name = "bracket_with_gusset"
export_step(part, "output.step")