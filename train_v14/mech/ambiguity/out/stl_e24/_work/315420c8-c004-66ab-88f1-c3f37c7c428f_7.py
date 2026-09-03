from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 3.0
gusset_height = 12.0
gusset_thickness = 4.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_rows = 2
hole_columns = 3

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as gp:
    with BuildSketch(Plane.YZ.offset(channel_length/2)) as sk:
        RegularPolygon(gusset_height, 3)
    extrude(amount=gusset_thickness)
gusset = gp.part

result = base + gusset

for i in range(hole_columns):
    for j in range(hole_rows):
        x = (i - (hole_columns-1)/2) * hole_spacing
        y = (j - (hole_rows-1)/2) * hole_spacing
        result = result - Pos(x, y, channel_height/2) * Cylinder(hole_diameter/2, channel_height + 10)

part = result
part.name = "channel_with_gusset"
export_step(part, "output.step")