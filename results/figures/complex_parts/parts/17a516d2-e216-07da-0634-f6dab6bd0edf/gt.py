from build123d import *

leg_a_length = 70.0
leg_b_length = 60.0
wall_thickness = 8.0
bracket_height = 12.0
hole_diameter = 6.0
rib_width = 8.0
rib_length = 16.0
chamfer_size = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_a_length,0), (leg_a_length,wall_thickness), (wall_thickness,wall_thickness), (wall_thickness,leg_b_length), (0,leg_b_length), (0,0), close=True)
        make_face()
    extrude(amount=bracket_height)

solid = p.part
rib = Pos(wall_thickness/2, wall_thickness/2, bracket_height/2) * Box(rib_length, rib_width, bracket_height)
solid = solid + rib

for x, y in [(leg_a_length/2, wall_thickness/2), (wall_thickness/2, leg_b_length/2)]:
    solid = solid - Pos(x, y, bracket_height/2) * Cylinder(hole_diameter/2, bracket_height)

vertical_edges = solid.edges().filter_by(Axis.Z)
target_edge = [e for e in vertical_edges if abs(e.center().X - wall_thickness) < 0.5 and abs(e.center().Y - wall_thickness) < 0.5][0]
solid = chamfer([target_edge], chamfer_size)

part = solid
part.name = "L_Bracket"
export_step(part, OUTPUT_PATH)