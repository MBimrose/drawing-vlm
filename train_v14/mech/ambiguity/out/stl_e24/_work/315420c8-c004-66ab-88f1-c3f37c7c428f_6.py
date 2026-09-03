from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 3.0
rib_height = 15.0
rib_thickness = 4.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_rows = 2
hole_columns = 3

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as rib_bp:
    with BuildSketch(Plane.YZ) as sk:
        RegularPolygon(rib_height/2, 3)
    extrude(amount=rib_thickness)
rib = Pos(channel_length/2, 0, channel_height/2) * rib_bp.part

result = base + rib

x_start = -((hole_columns - 1) * hole_spacing) / 2
y_start = -((hole_rows - 1) * (channel_width - 2 * wall_thickness)) / 2
for i in range(hole_columns):
    for j in range(hole_rows):
        px = x_start + i * hole_spacing
        py = y_start + j * (channel_width - 2 * wall_thickness)
        result = result - Pos(px, py, channel_height/2) * Cylinder(hole_diameter/2, channel_height + 10)

part = result
part.name = "channel_with_rib_and_holes"
export_step(part, "output.step")