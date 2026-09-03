from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 20.0
wall_thickness = 2.0
base_thickness = 4.0
rib_width = 8.0
rib_height = 12.0
rib_offset = 5.0
hole_diameter = 6.0
hole_spacing = 12.0
hole_edge_margin = 6.0
fillet_radius = 0.5
vent_slot_width = 30.0
vent_slot_height = 4.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
cavity_depth = outer_height - base_thickness - wall_thickness

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

cavity = Pos(0, 0, outer_height - cavity_depth/2) * Box(inner_length, inner_width, cavity_depth)
solid_body = solid_body - cavity

rib_x = -outer_length/2 + wall_thickness + rib_width/2
rib = Pos(rib_x, 0, rib_height/2) * Box(rib_width, inner_width - 2*wall_thickness, rib_height)
solid_body = solid_body + rib

for i in range(5):
    hx = -outer_length/2 + wall_thickness + hole_edge_margin
    hy = -outer_width/2 + hole_edge_margin + i * hole_spacing
    solid_body = solid_body - Pos(hx, hy, outer_height/2) * Cylinder(hole_diameter/2, outer_height)

vent = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(vent_slot_width, wall_thickness, vent_slot_height)
solid_body = solid_body - vent

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

part = solid_body
part.name = "box_with_cavity_rib_holes_vent"
export_step(part, "output.step")