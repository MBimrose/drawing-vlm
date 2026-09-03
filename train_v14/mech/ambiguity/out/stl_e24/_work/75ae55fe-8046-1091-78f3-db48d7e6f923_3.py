from build123d import *

plate_width = 80.0
plate_height = 25.0
plate_thickness = 8.0
pocket_width = 30.0
pocket_height = 15.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 8.0
hole_edge_offset = 8.0
rib_width = 4.0
rib_height = 10.0
rib_thickness = 3.0
rib_spacing = 12.0

solid_body = Box(plate_width, plate_thickness, plate_height)
solid_body = solid_body - Box(pocket_width, plate_thickness, pocket_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole_r = hole_diameter / 2
hole_tool = Rot(90, 0, 0) * Cylinder(hole_r, plate_thickness + 2)
for i in range(3):
    z = -hole_spacing + i * hole_spacing
    solid_body = solid_body - Pos(-plate_width/2 + hole_edge_offset, 0, z) * hole_tool
    solid_body = solid_body - Pos(plate_width/2 - hole_edge_offset, 0, z) * hole_tool

rib_count = int((plate_width - 2 * hole_edge_offset) // rib_spacing) + 1
rib_tool = Box(rib_width, rib_height, rib_thickness)
for i in range(rib_count):
    x = -plate_width/2 + hole_edge_offset + i * rib_spacing
    solid_body = solid_body + Pos(x, plate_thickness/2 + rib_height/2, rib_thickness/2) * rib_tool

part = solid_body
part.name = "plate_with_pocket_holes_ribs"
export_step(part, "output.step")