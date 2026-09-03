from build123d import *

outer_width = 60.0
outer_depth = 40.0
outer_height = 30.0
wall_thickness = 3.0
vent_slot_width = 8.0
vent_slot_height = 20.0
mount_hole_diameter = 3.0
chamfer_size = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vent_cut = Box(vent_slot_width, wall_thickness, vent_slot_height)
solid_body = solid_body - Pos(0, outer_depth/2 - wall_thickness/2, outer_height/2) * vent_cut
solid_body = solid_body - Pos(0, -outer_depth/2 + wall_thickness/2, outer_height/2) * vent_cut
solid_body = solid_body - Pos(outer_width/2 - wall_thickness/2, 0, outer_height/2) * Rot(0, 0, 90) * vent_cut
solid_body = solid_body - Pos(-outer_width/2 + wall_thickness/2, 0, outer_height/2) * Rot(0, 0, 90) * vent_cut

hole_cut = Cylinder(mount_hole_diameter/2, wall_thickness)
solid_body = solid_body - Pos(0, outer_depth/2 - wall_thickness/2, outer_height/2) * hole_cut
solid_body = solid_body - Pos(0, -outer_depth/2 + wall_thickness/2, outer_height/2) * hole_cut
solid_body = solid_body - Pos(outer_width/2 - wall_thickness/2, 0, outer_height/2) * Rot(0, 0, 90) * hole_cut
solid_body = solid_body - Pos(-outer_width/2 + wall_thickness/2, 0, outer_height/2) * Rot(0, 0, 90) * hole_cut

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "vented_enclosure"
export_step(part, "output.step")