from build123d import *

plate_length = 100.0
plate_width = 70.0
plate_thickness = 5.0
pocket_length = 60.0
pocket_width = 40.0
pocket_fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
rib_thickness = 2.0
rib_height = 3.0
chamfer_distance = 0.5

base = Box(plate_length, plate_width, plate_thickness)
pocket = Box(pocket_length, pocket_width, plate_thickness)
result = base - pocket

pocket_edges = result.edges().filter_by(Axis.Z)
result = fillet(pocket_edges, pocket_fillet_radius)

hole_positions = [
    (mount_hole_offset, mount_hole_offset),
    (plate_length - mount_hole_offset, mount_hole_offset),
    (mount_hole_offset, plate_width - mount_hole_offset),
    (plate_length - mount_hole_offset, plate_width - mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, plate_thickness)

rib = Box(rib_thickness, plate_width - 2 * rib_thickness, rib_height)
rib_left = Pos(-plate_length / 2 + rib_thickness / 2, 0, plate_thickness + rib_height / 2) * rib
rib_right = Pos(plate_length / 2 - rib_thickness / 2, 0, plate_thickness + rib_height / 2) * rib
result = result + rib_left + rib_right

top_face = result.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_distance)

part = result
part.name = "plate_with_pocket_ribs"
export_step(part, "output.step")