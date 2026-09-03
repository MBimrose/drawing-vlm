from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 6.0
pad_width = 40.0
pad_depth = 20.0
pad_height = 4.0
hole_diameter = 4.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
chamfer_size = 0.8
fillet_radius = 1.2

base = Pos(0, 0, plate_thickness / 2) * Box(plate_width, plate_depth, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

pad = Pos(0, 0, plate_thickness + pad_height / 2) * Box(pad_width, pad_depth, pad_height)
result = base + pad

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

total_h = plate_thickness + pad_height
for x, y in [(-hole_spacing_x, -hole_spacing_y/2), (0, -hole_spacing_y/2), (hole_spacing_x, -hole_spacing_y/2),
             (-hole_spacing_x, hole_spacing_y/2), (0, hole_spacing_y/2), (hole_spacing_x, hole_spacing_y/2)]:
    result = result - Pos(x, y, total_h / 2) * Cylinder(hole_diameter / 2, total_h + 2)

part = result
part.name = "plate_with_pad_and_holes"
export_step(part, "output.step")