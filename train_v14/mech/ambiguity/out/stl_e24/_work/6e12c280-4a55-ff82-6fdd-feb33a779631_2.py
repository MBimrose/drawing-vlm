from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
gusset_height = 30.0
gusset_extension = 20.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.5
slot_width = 4.0
slot_length = 30.0
slot_offset = 10.0

base = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as gp:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((0, 0), (gusset_extension, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=plate_thickness)
gusset = Pos(plate_length / 2, -gusset_height / 2, -plate_thickness / 2) * gp.part

result = base + gusset

slot = Pos(0, slot_offset, -plate_thickness / 2) * Box(slot_width, slot_length, plate_thickness)
result = result - slot

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_gusset"
export_step(part, "output.step")