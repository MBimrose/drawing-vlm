from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
thickness = 8.0
width = 12.0
fillet_radius = 3.0
blind_hole_diameter = 6.0
blind_hole_depth = 10.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
pocket_length = 20.0
pocket_width = 6.0
pocket_depth = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_leg_length, 0), (horizontal_leg_length, thickness),
                     (thickness, thickness), (thickness, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=width)

solid = p.part
inner_edge = solid.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
solid = fillet([inner_edge], fillet_radius)

solid = solid - Pos(thickness/2, vertical_leg_length/2, width - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

for x in [horizontal_leg_length/2 - mount_hole_spacing/2, horizontal_leg_length/2 + mount_hole_spacing/2]:
    solid = solid - Pos(x, thickness/2, width/2) * Cylinder(mount_hole_diameter/2, width)

solid = solid - Pos(horizontal_leg_length - pocket_length/2, thickness/2, pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")