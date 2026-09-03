from build123d import *
import math

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 80.0
groove_width = 2.0
groove_depth = 1.5
groove_turns = 3
groove_pitch = length / groove_turns
mount_hole_diameter = 4.0
chamfer_size = 0.5

solid_body = Cylinder(outer_radius, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

with BuildPart() as gp:
    with BuildSketch(Plane.XZ) as gs:
        with BuildLine() as gl:
            Polyline((inner_radius, 0), (inner_radius - groove_depth, groove_width/2),
                     (inner_radius - groove_depth, -groove_width/2), close=True)
        make_face()
    extrude(amount=length, taper=groove_turns * 360)
groove_solid = gp.part

solid_body = solid_body - groove_solid

hole_radius = mount_hole_diameter / 2
hole_center_radius = outer_radius - wall_thickness / 2
for i in range(4):
    angle = math.radians(i * 90)
    px = hole_center_radius * math.cos(angle)
    py = hole_center_radius * math.sin(angle)
    hole = Pos(px, py, 0) * Rot(0, 90, i * 90) * Cylinder(hole_radius, wall_thickness + 1)
    solid_body = solid_body - hole

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_groove"
export_step(part, "output.step")