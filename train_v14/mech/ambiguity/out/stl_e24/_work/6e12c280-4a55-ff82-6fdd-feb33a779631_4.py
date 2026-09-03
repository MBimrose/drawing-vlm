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
slot_width = 3.0
slot_length = 12.0
slot_spacing = 20.0
chamfer_distance = 0.5

base = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as gp:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((0, 0), (gusset_length, 0), (0, gusset_width), close=True)
        make_face()
    extrude(amount=plate_thickness)
gusset = Pos(plate_length / 2, -gusset_width / 2, -plate_thickness / 2) * gp.part

result = base + gusset

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness)

for i in range(2):
    y = (i - 0.5) * slot_spacing
    result = result - Pos(0, y, -plate_thickness / 2 + plate_thickness / 4) * Box(slot_width, slot_length, plate_thickness / 2)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "plate_with_gusset"
export_step(part, "output.step")