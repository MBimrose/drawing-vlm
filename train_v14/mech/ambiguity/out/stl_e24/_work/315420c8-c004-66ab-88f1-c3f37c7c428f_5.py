from build123d import *

chute_length = 80.0
chute_width = 30.0
chute_height = 20.0
wall_thickness = 3.0
rib_height = 12.0
rib_thickness = 4.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3

base = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
hollow = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as rib_bp:
    with BuildSketch(Plane.YZ) as sk:
        RegularPolygon(rib_height, 3)
    extrude(amount=rib_thickness)
rib = Pos(chute_length/2, 0, chute_height/2) * rib_bp.part

result = hollow + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, chute_height/2) * Cylinder(hole_diameter/2, chute_height)

part = result
part.name = "chute_with_rib_and_holes"
export_step(part, "output.step")