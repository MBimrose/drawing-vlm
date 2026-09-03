from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
leg_thickness = 12.0
bracket_depth = 12.0
inner_fillet_radius = 2.0
clearance_hole_diameter = 6.0
clearance_hole_offset_x = 30.0
clearance_hole_offset_y = 6.0
mount_hole_diameter = 5.0
mount_hole_spacing = 20.0
mount_hole_count = 3
mount_hole_start_y = 15.0
rib_width = 8.0
rib_height = 8.0
rib_thickness = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (leg_thickness, vertical_leg_length),
                     (leg_thickness, leg_thickness), (horizontal_leg_length, leg_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

solid_body = solid_body - Pos(clearance_hole_offset_x, clearance_hole_offset_y, bracket_depth/2) * Cylinder(clearance_hole_diameter/2, bracket_depth)

for i in range(mount_hole_count):
    y = mount_hole_start_y + i * mount_hole_spacing
    solid_body = solid_body - Pos(leg_thickness/2, y, bracket_depth/2) * Cylinder(mount_hole_diameter/2, bracket_depth)

rib = Pos(leg_thickness/2, leg_thickness/2, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")