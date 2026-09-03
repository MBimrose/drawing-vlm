from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
leg_thickness = 8.0
bracket_depth = 12.0
inner_fillet_radius = 3.0
blind_hole_diameter = 6.0
blind_hole_depth = 10.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
pocket_width = 20.0
pocket_height = 6.0
pocket_depth = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid = p.part
inner_edge = solid.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
solid = fillet([inner_edge], inner_fillet_radius)

solid = solid - Pos(leg_thickness/2, vertical_leg_length/2, bracket_depth - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

for x in [horizontal_leg_length/2 - mount_hole_spacing/2, horizontal_leg_length/2 + mount_hole_spacing/2]:
    solid = solid - Pos(x, leg_thickness/2, bracket_depth/2) * Cylinder(mount_hole_diameter/2, bracket_depth)

solid = solid - Pos(horizontal_leg_length - pocket_width/2, leg_thickness/2, pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")