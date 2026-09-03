from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
rib_height = 4.0
rib_thickness = 5.0
pocket_radius = 12.0
pocket_depth = 4.0
pocket_offset_x = 20.0
pocket_offset_y = 0.0
fillet_radius = 2.0

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Box(plate_length, rib_thickness, rib_height)
rib2 = Box(rib_thickness, plate_width, rib_height)
ribs = rib1 + rib2
plate_with_ribs = base + ribs

pocket = Pos(pocket_offset_x, pocket_offset_y, plate_thickness/2 - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)
result = plate_with_ribs - pocket

vertical_edges = result.edges().filter_by(Axis.Z)
result = fillet(vertical_edges, fillet_radius)

part = result
part.name = "plate_with_ribs_and_pocket"
export_step(part, "output.step")