from build123d import *

overall_length = 80.0
overall_width = 40.0
overall_height = 20.0
wall_thickness = 2.0
bearing_diameter = 15.0
vent_slot_width = 4.0
vent_slot_length = 30.0
fillet_radius = 3.0
mount_hole_diameter = 5.0
mount_hole_spacing = 60.0
rib_height = 4.0
rib_width = 10.0
rib_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-overall_length/2, -overall_width/2), (overall_length/2, -overall_width/2))
            l2 = Line(l1@1, (overall_length/2, overall_width/2))
            a1 = ThreePointArc(l2@1, (0, overall_width/2 + 5), (-overall_length/2, overall_width/2))
            l3 = Line(a1@1, l1@0)
        make_face()
    extrude(amount=overall_height)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

solid_body = solid_body - Pos(0, -overall_width/2 + wall_thickness/2, 0) * Box(vent_slot_length, wall_thickness, vent_slot_width)
solid_body = solid_body - Pos(-overall_length/2 + wall_thickness/2, 0, 0) * Rot(90, 0, 0) * Cylinder(bearing_diameter/2, overall_width + 10)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, overall_height + 10)

rib = Pos(-overall_length/2 + rib_offset + rib_width/2, -overall_width/2 + rib_offset + rib_height/2, overall_height/2) * Box(rib_width, rib_height, overall_height - 2*wall_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "hollow_box_with_rib"
export_step(part, "output.step")