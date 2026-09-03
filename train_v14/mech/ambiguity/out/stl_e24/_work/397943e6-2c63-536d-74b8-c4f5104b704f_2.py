from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 12.0
corner_radius = 6.0
tab_width = 10.0
tab_height = 12.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_depth_cut = 6.0
hole_diameter = 3.5
csk_diameter = 5.5
csk_angle = 82.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 4

base = Box(plate_width, plate_depth, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), corner_radius)

tab_left = Pos(-plate_width/2 - tab_height/2, 0, 0) * Box(tab_height, tab_width, plate_thickness)
tab_right = Pos(plate_width/2 + tab_height/2, 0, 0) * Box(tab_height, tab_width, plate_thickness)
base = base + tab_left + tab_right

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
base = base - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, csk_diameter/2, plate_thickness, csk_angle)
        base = base - hole

part = base
part.name = "plate_with_tabs_pocket_and_holes"
export_step(part, "output.step")