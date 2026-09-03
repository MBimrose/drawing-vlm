from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 6.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = plate_thickness + boss_height
hole_diameter = 4.0
hole_depth = 6.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
fillet_radius = 2.0
chamfer_distance = 1.0

base = Box(plate_length, plate_width, plate_thickness)
boss = Cylinder(boss_diameter / 2, boss_height)
result = base + boss

vertical_edges = result.edges().filter_by(Axis.Z)
result = fillet(vertical_edges, fillet_radius)

bottom_face = result.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
result = chamfer(bottom_edges, chamfer_distance)

pocket = Pos(0, 0, plate_thickness - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, plate_thickness - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)
        result = result - hole

part = result
part.name = "plate_with_boss_pocket_and_holes"
export_step(part, "output.step")