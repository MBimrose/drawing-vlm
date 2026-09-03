from build123d import *

leg_length_horizontal = 80.0
leg_length_vertical = 60.0
leg_thickness = 10.0
bracket_depth = 10.0
inner_fillet_radius = 2.0
outer_fillet_radius = 4.0
mount_hole_diameter = 4.0
mount_hole_offset = 15.0
counterbore_hole_diameter = 5.0
counterbore_diameter = 8.0
counterbore_depth = 3.0
counterbore_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length_horizontal, 0), (leg_length_horizontal, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length_vertical),
                     (0, leg_length_vertical), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid = p.part
solid = fillet(solid.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2], inner_fillet_radius)
solid = fillet(solid.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:], outer_fillet_radius)

solid = solid - Pos(mount_hole_offset, leg_length_vertical/2, bracket_depth/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, leg_length_vertical + 10)
solid = solid - Pos(leg_length_horizontal/2, counterbore_offset, bracket_depth/2) * Rot(0, -90, 0) * Cylinder(counterbore_hole_diameter/2, leg_length_horizontal + 10)
solid = solid - Pos(leg_length_horizontal - counterbore_depth/2, counterbore_offset, bracket_depth/2) * Rot(0, -90, 0) * Cylinder(counterbore_diameter/2, counterbore_depth)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")