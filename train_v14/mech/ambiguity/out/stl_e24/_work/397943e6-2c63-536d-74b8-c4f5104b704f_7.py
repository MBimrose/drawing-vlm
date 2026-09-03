from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 12.0
corner_radius = 6.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 6.0
hole_diameter = 3.5
countersink_diameter = 5.5
countersink_angle = 82.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = 20.0
hole_spacing_y = 15.0
rib_thickness = 4.0
rib_height = 10.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

rib1 = Pos(plate_length/2 + rib_thickness/2, 0, plate_thickness/2) * Box(rib_thickness, rib_height, plate_thickness)
rib2 = Pos(-plate_length/2 - rib_thickness/2, 0, plate_thickness/2) * Box(rib_thickness, rib_height, plate_thickness)
solid_body = solid_body + rib1 + rib2

start_x = -((hole_cols - 1) * hole_spacing_x) / 2
start_y = -((hole_rows - 1) * hole_spacing_y) / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = start_x + i * hole_spacing_x
        y = start_y + j * hole_spacing_y
        hole = Pos(x, y, plate_thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)
        solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_pocket_ribs_and_holes"
export_step(part, "output.step")