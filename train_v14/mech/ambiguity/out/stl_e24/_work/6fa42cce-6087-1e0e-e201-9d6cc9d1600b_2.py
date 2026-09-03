from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
corner_fillet_radius = 4.0
edge_chamfer = 1.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 3.0
slot_length = 30.0
slot_width = 10.0
hole_diameter = 6.0
countersink_diameter = 10.0
countersink_angle = 82.0
hole_spacing_x = 40.0
hole_spacing_y = 20.0
rib_height = 2.0
rib_width = 8.0
rib_length = 20.0
groove_width = 3.0
groove_depth = 2.0
groove_offset = 8.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)
solid_body = chamfer(solid_body.edges().filter_by(Axis.X) + solid_body.edges().filter_by(Axis.Y), edge_chamfer)

solid_body = solid_body - Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - Box(slot_length, slot_width, plate_thickness)

hole_positions = [(-hole_spacing_x/2, -hole_spacing_y/2), (hole_spacing_x/2, -hole_spacing_y/2),
                  (-hole_spacing_x/2, hole_spacing_y/2), (hole_spacing_x/2, hole_spacing_y/2)]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)

solid_body = solid_body + Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 - groove_depth/2) * Box(plate_length - 2*groove_offset, groove_width, groove_depth)

part = solid_body
part.name = "plate_with_features"
export_step(part, "output.step")