from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_outer_radius = 30.0
frame_inner_radius = 25.0
frame_height = 8.0
chamfer_size = 0.5
mount_hole_diameter = 4.0
mount_hole_offset_x = 20.0
mount_hole_offset_y = 15.0
central_hole_diameter = 5.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

frame_outer = Pos(0, 0, base_thickness + frame_height/2) * Cylinder(frame_outer_radius, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height/2) * Cylinder(frame_inner_radius, frame_height)
frame = frame_outer - frame_inner

result = base + frame

hole_height = base_thickness + frame_height + 10
for x, y in [(-mount_hole_offset_x, -mount_hole_offset_y),
             (mount_hole_offset_x, -mount_hole_offset_y),
             (-mount_hole_offset_x, mount_hole_offset_y),
             (mount_hole_offset_x, mount_hole_offset_y)]:
    result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(mount_hole_diameter/2, hole_height)

result = result - Pos(0, 0, base_thickness + frame_height/2) * Cylinder(central_hole_diameter/2, hole_height)

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")