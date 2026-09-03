from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
leg_width = 12.0
bracket_thickness = 12.0
fillet_radius = 2.0
clearance_hole_diameter = 6.0
clearance_hole_offset = 30.0
mount_hole_diameter = 5.0
mount_hole_spacing = 20.0
mount_hole_start_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (0, vertical_leg_length), (leg_width, vertical_leg_length),
                     (leg_width, leg_width), (horizontal_leg_length, leg_width),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid = p.part

# Fillet inner corner edge at (leg_width, leg_width)
inner_edges = [e for e in solid.edges() if abs(e.center().X - leg_width) < 0.1 and abs(e.center().Y - leg_width) < 0.1]
solid = fillet(inner_edges, fillet_radius)

# Clearance hole on horizontal leg
solid = solid - Pos(clearance_hole_offset, leg_width/2, bracket_thickness/2) * Cylinder(clearance_hole_diameter/2, bracket_thickness)

# Mount holes on vertical leg
for i in range(3):
    y = mount_hole_start_offset + i * mount_hole_spacing
    solid = solid - Pos(leg_width/2, y, bracket_thickness/2) * Cylinder(mount_hole_diameter/2, bracket_thickness)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")