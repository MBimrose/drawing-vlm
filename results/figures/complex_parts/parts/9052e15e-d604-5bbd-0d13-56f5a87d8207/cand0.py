from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
leg_thickness = 8.0
bracket_depth = 20.0
inner_fillet_radius = 2.0
rib_thickness = 3.0
rib_height = 6.0
rib_length = 20.0
hole_diameter = 5.0
cbore_diameter = 8.0
cbore_depth = 3.0
hole_spacing = 30.0
hole_offset_from_inner = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length + leg_thickness),
                     (0, vertical_leg_length + leg_thickness), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X) < 1e-3 and abs(e.center().Y) < 1e-3]
solid_body = fillet(inner_edges, inner_fillet_radius)

rib = Pos(rib_thickness/2, vertical_leg_length + leg_thickness + rib_length/2, bracket_depth/2) * Box(rib_thickness, rib_length, rib_height)
solid_body = solid_body + rib

for i in range(2):
    hx = hole_offset_from_inner + i * hole_spacing
    hy = leg_thickness / 2
    solid_body = solid_body - Pos(hx, hy, 0) * Cylinder(hole_diameter/2, bracket_depth + 1)
    solid_body = solid_body - Pos(hx, hy, 0) * Cylinder(cbore_diameter/2, cbore_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")