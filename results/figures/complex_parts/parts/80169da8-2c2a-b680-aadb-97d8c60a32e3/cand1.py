from build123d import *

outer_diameter = 80.0
wall_thickness = 2.0
height = 30.0
rib_thickness = 1.0
rib_height = 10.0
vent_slot_width = 3.0
vent_slot_height = 12.0
vent_slot_count = 4
mount_hole_diameter = 3.0
mount_hole_spacing = 40.0
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, inner_radius + rib_thickness/2, 0) * Box(2*inner_radius, rib_thickness, rib_height)
solid_body = solid_body + rib

for i in range(vent_slot_count):
    angle = i * 360.0 / vent_slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness/2, 0, height/2) * Box(wall_thickness + 0.2, vent_slot_height, vent_slot_width)
    solid_body = solid_body - slot

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, 2*outer_radius)
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "vented_cylinder_with_rib"
export_step(part, "output.step")