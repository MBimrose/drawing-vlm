from build123d import *

outer_diameter = 80.0
inner_diameter = 60.0
housing_length = 70.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
slot_width = 20.0
slot_depth = 30.0
slot_height = 15.0
hole_diameter = 5.0
hole_spacing = 30.0
chamfer_size = 2.0
rib_width = 10.0
rib_height = 20.0
rib_thickness = 5.0

solid_body = Cylinder(outer_diameter / 2.0, housing_length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_box = Pos(outer_diameter / 2.0 - slot_height / 2.0, 0, slot_height / 2.0) * Box(slot_width, slot_depth, slot_height)
solid_body = solid_body - slot_box

for x, y in [(-hole_spacing, 0), (hole_spacing, 0)]:
    solid_body = solid_body - Pos(x, y, housing_length / 2.0) * Cylinder(hole_diameter / 2.0, housing_length)

rib = Pos(outer_diameter / 2.0 - rib_thickness / 2.0, 0, rib_thickness / 2.0) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "housed_cylinder_with_slot_holes_rib"
export_step(part, "output.step")