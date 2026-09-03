from build123d import *

plate_length = 100
plate_width = 70
plate_thickness = 5
window_length = 60
window_width = 40
window_fillet_radius = 2
hole_diameter = 4
hole_offset = 10
rib_thickness = 2
rib_height = 3
rib_length = plate_width - 2 * hole_offset
rib_offset = plate_length / 2 - rib_thickness / 2

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = solid_body - Box(window_length, window_width, plate_thickness)

window_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X) < plate_length/2 - 1]
solid_body = fillet(window_edges, window_fillet_radius)

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib1 = Pos(rib_offset, 0, plate_thickness + rib_height/2) * Box(rib_thickness, rib_length, rib_height)
rib2 = Pos(-rib_offset, 0, plate_thickness + rib_height/2) * Box(rib_thickness, rib_length, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_window_ribs"
export_step(part, "output.step")