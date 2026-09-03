from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_height = 10.0
frame_thickness = 4.0
inner_length = base_length - 2 * frame_thickness
inner_width = base_width - 2 * frame_thickness
hole_diameter = 5.5
hole_spacing_x = 30.0
hole_spacing_y = 20.0
chamfer_size = 0.8

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
frame = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
inner_cut = Pos(0, 0, base_thickness + frame_height/2) * Box(inner_length, inner_width, frame_height)

solid_body = base + frame - inner_cut

hole_positions = [
    (-hole_spacing_x, -hole_spacing_y),
    (0, -hole_spacing_y),
    (hole_spacing_x, -hole_spacing_y),
    (-hole_spacing_x, hole_spacing_y),
    (0, hole_spacing_y),
    (hole_spacing_x, hole_spacing_y),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, (base_thickness + frame_height)/2) * Cylinder(hole_diameter/2, base_thickness + frame_height + 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "base_plate_with_frame"
export_step(part, "output.step")