from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
leg_thickness = 10.0
bracket_depth = 10.0
counterbore_diameter = 8.0
counterbore_depth = 4.0
through_hole_diameter = 4.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0
pocket_width = 20.0
pocket_length = 30.0
pocket_depth = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_leg_length,0), (horizontal_leg_length,leg_thickness),
                     (leg_thickness,leg_thickness), (leg_thickness,vertical_leg_length),
                     (0,vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid = p.part

cb_x, cb_y = leg_thickness/2, vertical_leg_length/2
solid = solid - Pos(cb_x, cb_y, bracket_depth - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid = solid - Pos(cb_x, cb_y, bracket_depth/2) * Cylinder(through_hole_diameter/2, bracket_depth)

for x, y in [(horizontal_leg_length/2 - mount_hole_spacing/2, 0),
             (horizontal_leg_length/2 + mount_hole_spacing/2, 0)]:
    solid = solid - Pos(x, y, bracket_depth/2) * Cylinder(mount_hole_diameter/2, bracket_depth)

pocket_x = horizontal_leg_length/2
pocket_y = leg_thickness/2
solid = solid - Pos(pocket_x, pocket_y, bracket_depth - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")