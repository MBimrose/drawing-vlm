from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 60.0
bracket_thickness = 10.0
inner_fillet_radius = 2.0
clearance_hole_diameter = 6.0
clearance_hole_offset = 5.0
blind_hole_diameter = 5.0
blind_hole_depth = 5.0
blind_hole_spacing = 20.0
blind_hole_start_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_leg_length,0), (horizontal_leg_length,bracket_thickness),
                     (bracket_thickness,bracket_thickness), (bracket_thickness,vertical_leg_length),
                     (0,vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - bracket_thickness) < 0.1 and abs(e.center().Y - bracket_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

solid_body = solid_body - Pos(clearance_hole_offset, vertical_leg_length, bracket_thickness/2) * Rot(90, 0, 0) * Cylinder(clearance_hole_diameter/2, 100)

for i in range(3):
    x = blind_hole_start_offset + i * blind_hole_spacing
    solid_body = solid_body - Pos(x, bracket_thickness/2, bracket_thickness - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")