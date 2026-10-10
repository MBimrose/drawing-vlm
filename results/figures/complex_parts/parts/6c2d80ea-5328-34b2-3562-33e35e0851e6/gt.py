from build123d import *

leg1_length = 80.0
leg2_length = 60.0
leg_thickness = 10.0
bracket_thickness = 8.0
gusset_thickness = 8.0
gusset_size = leg_thickness
hole_diameter = 4.0
hole_depth = 4.0
hole_spacing = 15.0
chamfer = 0.5

vertical = Pos(0, leg1_length/2, 0) * Box(leg_thickness, leg1_length, bracket_thickness)
horizontal = Pos(leg2_length/2, leg_thickness/2, 0) * Box(leg2_length, leg_thickness, bracket_thickness)
base = vertical + horizontal

with BuildPart() as gp:
    with BuildSketch() as gs:
        with BuildLine():
            Polyline((0,0), (gusset_size, 0), (0, gusset_size), close=True)
        make_face()
    extrude(amount=gusset_thickness)
gusset = gp.part
combined = base + gusset

for i in range(1, 4):
    combined = combined - Pos(i*hole_spacing, leg_thickness/2, bracket_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

edges = combined.edges().filter_by(Axis.Z)
combined = chamfer(edges, chamfer)

part = combined
part.name = "L_Mount_Bracket"
export_step(part, OUTPUT_PATH)