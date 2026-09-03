from build123d import *

knob_length = 70.0
knob_width = 20.0
knob_height = 25.0
wall_thickness = 2.0
end_radius = 8.0
blind_hole_diameter = 6.0
blind_hole_depth = knob_height - end_radius
chamfer_size = 0.5
rib_width = 10.0
rib_height = 4.0
rib_thickness = 1.0
side_hole_diameter = 4.0
side_hole_spacing = 15.0
side_hole_offset = 12.0

solid_body = Box(knob_length, knob_width, knob_height)
solid_body = offset(solid_body, amount=-wall_thickness)

end_faces = solid_body.faces().filter_by(Axis.X)
end_edges = []
for f in end_faces:
    end_edges.extend(f.edges())
solid_body = fillet(end_edges, end_radius)

rib = Pos(0, 0, knob_height/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

blind_hole = Pos(0, 0, knob_height/2 - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - blind_hole

for x in [side_hole_offset, side_hole_offset + side_hole_spacing]:
    side_hole = Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(side_hole_diameter/2, knob_width + 10)
    solid_body = solid_body - side_hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "knob"
export_step(part, "output.step")