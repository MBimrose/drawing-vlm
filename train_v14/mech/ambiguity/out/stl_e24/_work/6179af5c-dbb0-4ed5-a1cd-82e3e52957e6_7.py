from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 15.0
wall_thickness = 2.0
rib_width = 6.0
rib_height = 3.0
fillet_radius = 0.5
chamfer_distance = 0.5
hole_diameter = 3.0
hole_offset_from_end = 20.0
notch_width = 8.0
notch_depth = 4.0

base = Pos(0, 0, channel_length/2) * Box(channel_width, channel_height, channel_length)
rib = Pos(0, -channel_height/2 + rib_height/2, channel_length/2) * Box(rib_width, rib_height, channel_length)
solid_body = base + rib

inner_width = channel_width - 2 * wall_thickness
inner_height = channel_height - wall_thickness
inner_cut = Pos(0, wall_thickness/2, channel_length/2) * Box(inner_width, inner_height, channel_length)
solid_body = solid_body - inner_cut

solid_body = chamfer(solid_body.edges(), chamfer_distance)
solid_body = fillet(solid_body.edges(), fillet_radius)

hole_z = channel_length - hole_offset_from_end
hole_cyl = Pos(channel_width/2, 0, hole_z) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, channel_width + 10)
solid_body = solid_body - hole_cyl

notch_x = channel_width/2 - wall_thickness - notch_depth/2
notch_cut = Pos(notch_x, 0, channel_length/2) * Box(notch_depth, notch_width, notch_depth)
solid_body = solid_body - notch_cut

part = solid_body
part.name = "u_channel_with_rib"
export_step(part, "output.step")