from build123d import *

length = 80.0
width = 40.0
height = 20.0
wall_thickness = 2.0
rib_height = 5.0
fillet_radius = 3.0
mount_hole_dia = 5.0
mount_hole_spacing = 60.0
vent_slot_width = 4.0
vent_slot_height = 12.0
vent_slot_spacing = 8.0
pocket_length = 30.0
pocket_width = 15.0
pocket_depth = 10.0
pocket_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-length/2, -width/2), (length/2, -width/2))
            l2 = Line(l1@1, (length/2, width/2))
            arc = ThreePointArc(l2@1, (0, width/2 + rib_height), (-length/2, width/2))
            l3 = Line(arc@1, (-length/2, -width/2))
        make_face()
    extrude(amount=height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, height/2) * Cylinder(mount_hole_dia/2, height + 10)

pocket_center_x = -length/2 + pocket_offset + pocket_length/2
pocket_center_y = -width/2 + pocket_width/2
solid_body = solid_body - Pos(pocket_center_x, pocket_center_y, pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

num_slots = int((length - 2*wall_thickness) // vent_slot_spacing)
for i in range(num_slots):
    x_pos = -length/2 + wall_thickness + vent_slot_spacing/2 + i*vent_slot_spacing
    solid_body = solid_body - Pos(x_pos, -width/2 + wall_thickness/2, 0) * Box(vent_slot_width, wall_thickness, vent_slot_height)

part = solid_body
part.name = "hollow_box_with_rib"
export_step(part, "output.step")