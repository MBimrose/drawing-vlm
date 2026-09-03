from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_outer_length = 70.0
frame_outer_width = 50.0
frame_height = 12.0
frame_wall_thickness = 5.0
hole_diameter = 4.0
hole_spacing = 6.0
hole_count = 9
chamfer_size = 0.8
fillet_vertical = 1.2
fillet_top = 0.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_vertical)

frame_outer = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer_length, frame_outer_width, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer_length - 2*frame_wall_thickness, frame_outer_width - 2*frame_wall_thickness, frame_height)
frame = frame_outer - frame_inner

result = base + frame
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

hole_start_x = -((hole_count - 1) * hole_spacing) / 2.0
hole_positions = [(hole_start_x + i * hole_spacing, 0) for i in range(hole_count)]
for x, y in hole_positions:
    result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, base_thickness + frame_height + 20)

part = result
part.name = "base_with_frame_and_holes"
export_step(part, "output.step")