from build123d import *

leg_length = 80.0
leg_height = 70.0
thickness = 8.0
width = 12.0
fillet_radius = 4.0
hole_diameter = 6.0
hole_spacing = 20.0
pocket_diameter = 20.0
pocket_depth = 5.0

horizontal = Pos(leg_length/2, thickness/2, 0) * Box(leg_length, thickness, width)
vertical = Pos(thickness/2, leg_height/2, 0) * Box(thickness, leg_height, width)
base = horizontal + vertical

inner_edges = [e for e in base.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
base = fillet(inner_edges, fillet_radius)

with BuildPart() as g:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((0, 0), (thickness, 0), (0, thickness), close=True)
        make_face()
    extrude(amount=width)
gusset = g.part
base = base + gusset

for i in range(3):
    y = leg_height/2 + (i - 1) * hole_spacing
    base = base - Pos(thickness/2, y, 0) * Cylinder(hole_diameter/2, width + 1)

base = base - Pos(leg_length/2, thickness/2, width/2 - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)

part = base
part.name = "L_Bracket"
export_step(part, "output.step")