from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 3.0
rib_height = 12.0
rib_width = 10.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as rib_bp:
    with BuildSketch(Plane.YZ) as sk:
        RegularPolygon(rib_width, 3)
    extrude(amount=wall_thickness)
rib = Pos(channel_length/2, 0, channel_height/2) * rib_bp.part

combined = base + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        combined = combined - Pos(x, y, channel_height/2) * Cylinder(hole_diameter/2, channel_height + 10)

part = combined
part.name = "channel_with_rib_and_holes"
export_step(part, "output.step")