from build123d import *

rail_length = 100.0
rail_width = 30.0
rail_height = 20.0
wall_thickness = 2.0
slot_width = 6.0
slot_height = rail_height - 2 * wall_thickness - 2.0
fillet_radius = 1.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset = 15.0
rib_thickness = 2.0
rib_height = rail_height - 2 * wall_thickness - 2.0

solid_body = Box(rail_length, rail_width, rail_height)
inner_box = Box(rail_length - 2*wall_thickness, rail_width - 2*wall_thickness, rail_height - 2*wall_thickness)
solid_body = solid_body - inner_box

slot_box = Box(rail_length, slot_width, slot_height)
solid_body = solid_body - slot_box

x_edges = solid_body.edges().filter_by(Axis.X)
solid_body = fillet(x_edges, fillet_radius)

num_holes = int((rail_length - 2 * hole_offset) // hole_spacing) + 1
for i in range(num_holes):
    x = -rail_length/2 + hole_offset + i * hole_spacing
    hole = Pos(x, rail_width/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, rail_width + 10)
    solid_body = solid_body - hole

rib = Box(rail_length, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "rail_with_slot_and_holes"
export_step(part, "output.step")