from build123d import *

length = 80.0
width = 40.0
height = 20.0
wall_thickness = 2.0
notch_width = 10.0
notch_depth = 12.0
fillet_radius = 3.0
mount_hole_diameter = 5.0
mount_hole_spacing = 60.0
vent_slot_width = 4.0
vent_slot_spacing = 8.0
vent_slot_count = 5
arc_height = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (length, 0))
            l2 = Line(l1 @ 1, (length, width))
            arc = ThreePointArc(l2 @ 1, (length/2, width + arc_height), (0, width))
            l3 = Line(arc @ 1, (0, 0))
        make_face()
    extrude(amount=height)

solid_body = p.part
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
notch = Pos(notch_width/2, notch_depth/2, height/2) * Box(notch_width, notch_depth, height)
solid_body = solid_body - notch
for x, y in [(-mount_hole_spacing/2, width/2), (mount_hole_spacing/2, width/2)]:
    solid_body = solid_body - Pos(x, y, height/2) * Cylinder(mount_hole_diameter/2, height)
for i in range(vent_slot_count):
    x_pos = length/2 + (i - (vent_slot_count-1)/2) * vent_slot_spacing
    slot = Pos(x_pos, wall_thickness, 0) * Box(vent_slot_width, wall_thickness*2, height)
    solid_body = solid_body - slot

part = solid_body
part.name = "vented_enclosure"
export_step(part, "output.step")