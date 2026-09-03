from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 12.0
corner_radius = 6.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 6.0
hole_diameter = 3.5
countersink_diameter = 5.5
countersink_angle = 82.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 4
rib_thickness = 4.0
rib_width = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(base_length, base_width)
    extrude(amount=base_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)

pocket = Pos(0, 0, base_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

rib_left = Pos(-base_length/2 - rib_thickness/2, 0, base_thickness/2) * Box(rib_thickness, rib_width, base_thickness)
rib_right = Pos(base_length/2 + rib_thickness/2, 0, base_thickness/2) * Box(rib_thickness, rib_width, base_thickness)
solid_body = solid_body + rib_left + rib_right

x_start = -((hole_cols - 1) * hole_spacing_x) / 2
y_start = -((hole_rows - 1) * hole_spacing_y) / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = x_start + i * hole_spacing_x
        y = y_start + j * hole_spacing_y
        hole = Pos(x, y, base_thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, base_thickness, countersink_angle)
        solid_body = solid_body - hole

part = solid_body
part.name = "base_plate_with_pocket_ribs_and_holes"
export_step(part, "output.step")