from build123d import *

horizontal_length = 80.0
vertical_length = 70.0
leg_width = 40.0
thickness = 5.0
boss_radius = 12.0
boss_height = 12.0
boss_hole_diameter = 8.0
counterbore_diameter = 14.0
counterbore_depth = 2.5
mount_hole_diameter = 6.0
mount_hole_spacing = 60.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-leg_width/2, 0),
                (horizontal_length, 0),
                (horizontal_length, leg_width),
                (leg_width/2, leg_width),
                (leg_width/2, vertical_length + leg_width),
                (-leg_width/2, vertical_length + leg_width),
                close=True
            )
        make_face()
    extrude(amount=thickness)

solid = p.part

boss_center_y = vertical_length + leg_width/2
boss = Pos(0, boss_center_y, thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
solid = solid + boss

cbore = Pos(0, boss_center_y, thickness + boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid = solid - cbore

through_hole = Pos(0, boss_center_y, (thickness + boss_height)/2) * Cylinder(boss_hole_diameter/2, thickness + boss_height + 20)
solid = solid - through_hole

for x, y in [(-mount_hole_spacing/2, leg_width/2), (mount_hole_spacing/2, leg_width/2)]:
    hole = Pos(x, y, thickness/2) * Cylinder(mount_hole_diameter/2, thickness + 20)
    solid = solid - hole

top_face = solid.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid = chamfer(top_edges, chamfer_size)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")