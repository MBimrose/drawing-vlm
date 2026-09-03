from build123d import *

outer_width = 80.0
outer_depth = 40.0
outer_height = 20.0
wall_thickness = 2.0
top_fillet_radius = 3.0
mount_hole_diameter = 5.0
mount_hole_spacing = 60.0
rib_width = 4.0
rib_height = 12.0
rib_spacing = 15.0
vent_slot_width = 4.0
vent_slot_height = 10.0
vent_spacing = 8.0
side_cutout_width = 20.0
side_cutout_height = 15.0
side_cutout_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-outer_width/2, -outer_depth/2), (outer_width/2, -outer_depth/2))
            l2 = Line(l1@1, (outer_width/2, outer_depth/2))
            arc = ThreePointArc(l2@1, (0, outer_depth/2 + 5), (-outer_width/2, outer_depth/2))
            l3 = Line(arc@1, (-outer_width/2, -outer_depth/2))
        make_face()
    extrude(amount=outer_height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), top_fillet_radius)

for x, y in [(-mount_hole_spacing/2, 0), (mount_hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, outer_height * 2)

rib_count = int((outer_width - 2*wall_thickness) // rib_spacing)
for i in range(rib_count):
    x_pos = -outer_width/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, -outer_depth/2 + wall_thickness + rib_height/2, wall_thickness + (outer_height - 2*wall_thickness)/2) * Box(rib_width, rib_height, outer_height - 2*wall_thickness)
    solid_body = solid_body + rib

vent_count = int((outer_width - 2*wall_thickness) // vent_spacing)
for i in range(vent_count):
    x_pos = -outer_width/2 + wall_thickness + vent_spacing/2 + i * vent_spacing
    vent = Pos(x_pos, -outer_depth/2 + wall_thickness/2, wall_thickness/2) * Box(vent_slot_width, vent_slot_height, wall_thickness)
    solid_body = solid_body - vent

cutout = Pos(-outer_width/2 + wall_thickness + side_cutout_width/2, -outer_depth/2 + side_cutout_depth/2, outer_height/2) * Box(side_cutout_width, side_cutout_depth, side_cutout_height)
solid_body = solid_body - cutout

part = solid_body
part.name = "hollow_box_with_ribs_and_vents"
export_step(part, "output.step")