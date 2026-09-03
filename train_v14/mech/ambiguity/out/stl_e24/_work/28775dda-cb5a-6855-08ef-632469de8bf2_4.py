from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
cutout_width = 40.0
cutout_depth = 30.0
hole_diameter = 4.0
hole_depth = 6.0
hole_pitch_x = 20.0
hole_pitch_y = 30.0
holes_x = 3
holes_y = 2
fillet_radius = 2.0
chamfer_size = 1.0

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = chamfer(solid_body.edges(), chamfer_size)

cutout = Box(cutout_width, cutout_depth, plate_thickness)
solid_body = solid_body - cutout

for i in range(holes_x):
    for j in range(holes_y):
        x = (i - (holes_x - 1) / 2) * hole_pitch_x
        y = (j - (holes_y - 1) / 2) * hole_pitch_y
        hole = Pos(x, y, plate_thickness / 2 - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)
        solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_cutout_and_holes"
export_step(part, "output.step")