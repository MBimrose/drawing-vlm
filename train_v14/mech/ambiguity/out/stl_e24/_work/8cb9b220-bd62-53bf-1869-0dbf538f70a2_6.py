from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
cable_slot_width = 12.0
cable_slot_height = 5.0
mount_hole_diameter = 2.0
mount_hole_spacing = 30.0
chamfer_size = 0.8
fillet_radius = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
inner_box = Pos(0, 0, outer_height/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, outer_height - 2*wall_thickness)
solid_body = solid_body - inner_box

slot_box = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(cable_slot_width, wall_thickness, cable_slot_height)
solid_body = solid_body - slot_box

for y_pos in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(-outer_length/2, y_pos, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length)
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "enclosure_with_cable_slot"
export_step(part, "output.step")