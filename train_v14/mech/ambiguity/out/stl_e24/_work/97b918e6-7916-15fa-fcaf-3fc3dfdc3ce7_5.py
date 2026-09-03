from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
leg_thickness = 12.0
bracket_depth = 12.0
inner_fillet_radius = 2.0
through_hole_diameter = 6.0
through_hole_offset_x = 30.0
through_hole_offset_y = 6.0
mount_hole_diameter = 5.0
mount_hole_spacing = 20.0
mount_hole_start_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (0, vertical_leg_length), (leg_thickness, vertical_leg_length),
                     (leg_thickness, leg_thickness), (horizontal_leg_length, leg_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid = p.part

inner_edge = solid.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
solid = fillet([inner_edge], inner_fillet_radius)

solid = solid - Pos(through_hole_offset_x, through_hole_offset_y, bracket_depth/2) * Cylinder(through_hole_diameter/2, bracket_depth)

for i in range(3):
    y = mount_hole_start_offset + i * mount_hole_spacing
    solid = solid - Pos(leg_thickness/2, y, bracket_depth/2) * Cylinder(mount_hole_diameter/2, bracket_depth)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")