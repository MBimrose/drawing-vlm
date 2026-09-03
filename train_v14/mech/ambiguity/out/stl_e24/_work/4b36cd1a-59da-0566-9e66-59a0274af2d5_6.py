from build123d import *
import math

outer_width = 80.0
outer_depth = 45.0
outer_height = 20.0
wall_thickness = 2.0
top_fillet_radius = 3.0
vent_hole_diameter = 4.0
vent_rows = 4
vent_cols = 5
vent_spacing_x = 12.0
vent_spacing_y = 8.0
mount_hole_diameter = 5.0
mount_hole_spacing = 60.0
rib_width = 10.0
rib_depth = 20.0
rib_height = outer_height - 2 * wall_thickness

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-outer_width/2, -outer_depth/2), (outer_width/2, -outer_depth/2))
            l2 = Line(l1@1, (outer_width/2, outer_depth/2 - 5))
            a1 = ThreePointArc(l2@1, (0, outer_depth/2), (-outer_width/2, outer_depth/2 - 5))
            l3 = Line(a1@1, (-outer_width/2, -outer_depth/2))
        make_face()
    extrude(amount=outer_height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), top_fillet_radius)

rib = Pos(-outer_width/2 + wall_thickness + rib_width/2, -outer_depth/2 + wall_thickness + rib_depth/2, rib_height/2) * Box(rib_width, rib_depth, rib_height)
solid_body = solid_body + rib

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_spacing_x
        z = (j - (vent_rows-1)/2) * vent_spacing_y
        solid_body = solid_body - Pos(x, -outer_depth/2 + wall_thickness/2, z) * Rot(90, 0, 0) * Cylinder(vent_hole_diameter/2, wall_thickness + 2)

part = solid_body
part.name = "vented_box_with_rib"
export_step(part, "output.step")