from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_height = 6.0
frame_thickness = 5.0
inner_length = base_length - 2 * frame_thickness
inner_width = base_width - 2 * frame_thickness
hole_diameter = 4.0
hole_spacing = 15.0
fillet_radius = 1.5
chamfer_distance = 0.8

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = fillet(bottom_face.edges(), chamfer_distance)

frame_outer = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_thickness, base_width - 2*frame_thickness, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height/2) * Box(inner_length - 2*frame_thickness, inner_width - 2*frame_thickness, frame_height)
frame = frame_outer - frame_inner
frame = fillet(frame.edges().filter_by(Axis.Z), fillet_radius)

combined = base + frame

hole_r = hole_diameter / 2
hole_h = base_thickness + frame_height + 10
hole_z = base_thickness/2 + frame_height/2
x_left = -(base_length - 2*frame_thickness)/2
x_right = (base_length - 2*frame_thickness)/2
y_front = -(base_width - 2*frame_thickness)/2
y_back = (base_width - 2*frame_thickness)/2

for y in [-hole_spacing/2, hole_spacing/2]:
    combined = combined - Pos(x_left, y, hole_z) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
    combined = combined - Pos(x_right, y, hole_z) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
for x in [-hole_spacing/2, hole_spacing/2]:
    combined = combined - Pos(x, y_front, hole_z) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)
    combined = combined - Pos(x, y_back, hole_z) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)

part = combined
part.name = "base_plate_with_frame"
export_step(part, "output.step")