from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
leg_thickness = 10.0
bracket_thickness = 8.0
inner_fillet_radius = 2.0
gusset_width = 12.0
gusset_height = 12.0
gusset_thickness = 4.0
hole_diameter = 4.0
hole_depth = 4.0
hole_spacing = 15.0
hole_offset_from_end = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, leg_length_long), (leg_thickness, leg_length_long),
                     (leg_thickness, leg_thickness), (leg_length_short, leg_thickness),
                     (leg_length_short, 0), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

with BuildPart() as g:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((0, 0), (gusset_width, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=gusset_thickness)

gusset_body = Pos(leg_thickness, leg_thickness, bracket_thickness) * g.part
solid_body = solid_body + gusset_body

for i in range(3):
    hx = hole_offset_from_end + i * hole_spacing
    hy = leg_thickness / 2
    hz = bracket_thickness - hole_depth / 2
    solid_body = solid_body - Pos(hx, hy, hz) * Cylinder(hole_diameter / 2, hole_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")