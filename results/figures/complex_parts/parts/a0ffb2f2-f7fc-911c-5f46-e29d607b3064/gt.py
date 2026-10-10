from build123d import *

link_body_length = 60.0
shank_radius = 5.0
eye_radius = 15.0
split_gap_width = 2.0
bolt_hole_diameter = 8.0
fillet_radius = 1.0
chamfer_distance = 0.5

# Shank: cylinder from Z=0 to Z=60
shank = Pos(0, 0, link_body_length / 2) * Cylinder(shank_radius, link_body_length)
top_face = shank.faces().sort_by(Axis.Z)[-1]
shank = fillet(top_face.edges(), fillet_radius)

# Eye: ring from Z=55 to Z=65
eye_center_z = link_body_length
eye_height = 2 * shank_radius
eye_outer = Pos(0, 0, eye_center_z) * Cylinder(eye_radius, eye_height)
eye_inner = Pos(0, 0, eye_center_z) * Cylinder(shank_radius, eye_height)
eye = eye_outer - eye_inner

# Union shank and eye
result = shank + eye

# Split: rectangular slot through the eye
split_box = Pos(0, 0, eye_center_z) * Box(2 * shank_radius, split_gap_width, 2 * eye_radius)
result = result - split_box

# Bolt hole: through the shank
bolt_hole = Pos(0, 0, link_body_length / 2) * Cylinder(bolt_hole_diameter / 2, link_body_length)
result = result - bolt_hole

# Chamfer edges parallel to X
x_edges = result.edges().filter_by(Axis.X)
result = chamfer(x_edges, chamfer_distance)

part = result
part.name = "ForgedLink"
export_step(part, OUTPUT_PATH)