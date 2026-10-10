from build123d import *
import math

cap_height = 30.0
base_diameter = 60.0
top_diameter = 50.0
lip_height = 10.0
lip_outer_diameter = 70.0
wall_thickness = 3.0
vent_radius = 5.0
vent_angle = 45.0
fillet_radius = 2.0

with BuildPart() as p1:
    with BuildSketch() as s1:
        Circle(base_diameter / 2)
    with BuildSketch(Plane.XY.offset(cap_height)) as s2:
        Circle(top_diameter / 2)
    loft()
body = p1.part

with BuildPart() as p2:
    with BuildSketch() as s3:
        Circle(top_diameter / 2)
    with BuildSketch(Plane.XY.offset(cap_height + lip_height)) as s4:
        Circle(lip_outer_diameter / 2)
    loft()
lip = p2.part

combined = body + lip
combined = fillet(combined.edges(), fillet_radius)

top_face = combined.faces().sort_by(Axis.Z)[-1]
combined = offset(combined, amount=-wall_thickness, openings=[top_face])

vent_center_radius = (top_diameter / 2 + lip_outer_diameter / 2) / 2
vent_x = vent_center_radius * math.cos(math.radians(vent_angle))
vent_y = vent_center_radius * math.sin(math.radians(vent_angle))
vent_z = cap_height / 2 + (cap_height + lip_height + 2) / 2
vent_cyl = Pos(vent_x, vent_y, vent_z) * Cylinder(vent_radius, cap_height + lip_height + 2)

part = combined - vent_cyl
part.name = "cap_with_vent"
export_step(part, OUTPUT_PATH)