from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 8.0
gusset_width = 20.0
gusset_height = 30.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.5
rib_thickness = 3.0
rib_width = 6.0
rib_spacing = 20.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_height, plate_thickness)

with BuildPart() as g:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((plate_width/2, -gusset_height/2), (plate_width/2 + gusset_width, -gusset_height/2), (plate_width/2, -gusset_height/2 + gusset_height), close=True)
        make_face()
    extrude(amount=plate_thickness)
gusset = g.part

result = base + gusset

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

rib1 = Pos(0, -rib_spacing/2, plate_thickness/4) * Box(rib_thickness, rib_width, plate_thickness/2)
rib2 = Pos(0, rib_spacing/2, plate_thickness/4) * Box(rib_thickness, rib_width, plate_thickness/2)
result = result + rib1 + rib2

part = result
part.name = "plate_with_gusset_ribs"
export_step(part, "output.step")