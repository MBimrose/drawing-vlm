from build123d import *

leg_length = 80.0
leg_thickness = 8.0
leg_width = 20.0
rib_thickness = 4.0
rib_height = 6.0
fillet_radius = 2.0
hole_diameter = 5.0
cbore_diameter = 8.0
cbore_depth = 3.0
hole_spacing = 30.0

vertical = Pos(leg_thickness/2, leg_length/2, leg_width/2) * Box(leg_thickness, leg_length, leg_width)
horizontal = Pos(leg_length/2, leg_thickness/2, leg_width/2) * Box(leg_length, leg_thickness, leg_width)
base = vertical + horizontal

rib = Pos(rib_thickness/2, leg_length/2, leg_width/2) * Box(rib_thickness, leg_length, rib_height)
base = base + rib

inner_edges = [e for e in base.edges() if abs(e.center().X) < 1e-3 and abs(e.center().Y) < 1e-3]
base = fillet(inner_edges, fillet_radius)

for x, y in [(leg_length/2 - hole_spacing/2, leg_thickness/2), (leg_length/2 + hole_spacing/2, leg_thickness/2)]:
    base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, leg_width + 1)
    base = base - Pos(x, y, 0) * Cylinder(cbore_diameter/2, cbore_depth)

part = base
part.name = "L_Bracket"
export_step(part, "output.step")