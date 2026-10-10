from build123d import *

overall_width = 80.0
overall_height = 30.0
wall_thickness = 5.0
flange_thickness = 4.0
extrude_depth = overall_height + wall_thickness
inner_radius = 10.0
fillet_radius = 3.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0
pocket_width = 12.0
pocket_height = 8.0
pocket_depth = 3.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-overall_width/2, 0), (-overall_width/2, overall_height))
            l2 = Line(l1@1, (overall_width/2, overall_height))
            l3 = Line(l2@1, (overall_width/2, overall_height - flange_thickness))
            l4 = Line(l3@1, (inner_radius + wall_thickness, overall_height - flange_thickness))
            a1 = ThreePointArc(l4@1, (inner_radius + wall_thickness, overall_height - flange_thickness - wall_thickness), (inner_radius, 0))
            l5 = Line(a1@1, (-inner_radius, 0))
            a2 = ThreePointArc(l5@1, (-inner_radius - wall_thickness, overall_height - flange_thickness - wall_thickness), (-inner_radius - wall_thickness, overall_height - flange_thickness))
            l6 = Line(a2@1, (-overall_width/2, overall_height - flange_thickness))
            l7 = Line(l6@1, (-overall_width/2, 0))
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part
solid_body = solid_body - Pos(0, overall_height/2, extrude_depth/2) * Cylinder(inner_radius - 0.5, extrude_depth)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, overall_height/2, extrude_depth/2) * Cylinder(mount_hole_diameter/2, extrude_depth)

for x in [-overall_width/4, overall_width/4]:
    solid_body = solid_body - Pos(x, overall_height/2, extrude_depth - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)

part = solid_body
part.name = "u_channel_with_pockets"
export_step(part, "output.step")