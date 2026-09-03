from build123d import *

base_width = 80.0
base_length = 60.0
base_thickness = 6.0
frame_height = 7.0
frame_thickness = 5.0
pocket_width = 40.0
pocket_length = 30.0
pocket_depth = 4.0
hole_diameter = 4.0
hole_spacing_x = 18.0
hole_spacing_y = 17.0
chamfer_size = 0.5
rib_width = 5.0
rib_height = 4.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_length, base_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

frame = Pos(0, 0, base_thickness + frame_height/2) * Box(base_width, base_length, frame_height)
inner_cut = Pos(0, 0, base_thickness + frame_height/2) * Box(base_width - 2*frame_thickness, base_length - 2*frame_thickness, frame_height)
frame = frame - inner_cut

rib = Pos(0, 0, base_thickness + rib_height/2) * Box(base_width, rib_width, rib_height)

result = base + frame + rib

pocket = Pos(0, 0, base_thickness + frame_height - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
result = result - pocket

hole_r = hole_diameter / 2
hole_h = base_thickness + frame_height + 2
for i in range(4):
    for j in range(2):
        x = (i - 1.5) * hole_spacing_x
        y = (j - 0.5) * hole_spacing_y * 2
        result = result - Pos(x, y, (base_thickness + frame_height)/2) * Cylinder(hole_r, hole_h)

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")