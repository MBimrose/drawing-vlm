from build123d import *

horizontal_length = 80.0
vertical_height = 55.0
leg_thickness = 12.0
bracket_depth = 10.0
inner_fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_from_end = 20.0
gusset = True

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_length, 0), (horizontal_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_height),
                     (0, vertical_height), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid = p.part
inner_edges = [e for e in solid.edges().filter_by(Axis.Z) if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid = fillet(inner_edges, inner_fillet_radius)

solid = solid - Pos(horizontal_length/2 - hole_offset_from_end, leg_thickness/2, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth)
solid = solid - Pos(leg_thickness/2, vertical_height/2 - hole_offset_from_end, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth)

if gusset:
    with BuildPart() as gp:
        with BuildSketch() as gsk:
            with BuildLine() as gbl:
                Polyline((0,0), (leg_thickness, 0), (0, leg_thickness), close=True)
            make_face()
        extrude(amount=bracket_depth)
    solid = solid + gp.part

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")