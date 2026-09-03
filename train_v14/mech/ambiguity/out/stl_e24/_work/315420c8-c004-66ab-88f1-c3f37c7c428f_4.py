from build123d import *

length = 80.0
width = 30.0
height = 20.0
wall_thickness = 3.0
rib_height = 12.0
rib_thickness = 4.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3

base = Box(length, width, height)
top_face = base.faces().sort_by(Axis.Z)[-1]
hollow = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as rib_bp:
    with BuildSketch(Plane.YZ.offset(length/2)) as sk:
        RegularPolygon(rib_height, 3)
    extrude(amount=rib_thickness)
rib = rib_bp.part

result = hollow + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, height*2)

part = result
part.name = "hollow_box_with_rib_and_holes"
export_step(part, "output.step")