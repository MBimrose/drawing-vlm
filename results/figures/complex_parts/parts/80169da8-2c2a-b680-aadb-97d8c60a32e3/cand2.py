from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 2.0
height = 30.0
tab_width = 15.0
tab_height = 10.0
tab_thickness = wall_thickness
chamfer_size = 0.5
hole_diameter = 3.0
hole_count = 4
hole_z = height * 0.6
slot_width = 5.0
slot_height = 12.0
slot_depth = wall_thickness + 0.2

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Pos(0, 0, height/2) * Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

tab = Pos(0, outer_radius + tab_thickness/2, 0) * Box(height, tab_thickness, tab_width)
tab = chamfer(tab.edges(), chamfer_size)
solid_body = solid_body + tab

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = (outer_radius - wall_thickness/2) * math.cos(angle)
    py = (outer_radius - wall_thickness/2) * math.sin(angle)
    hole = Pos(px, py, hole_z) * Rot(0, 0, angle) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, wall_thickness + 0.2)
    solid_body = solid_body - hole

slot = Pos(0, outer_radius - wall_thickness/2, height/2) * Box(slot_width, slot_depth, slot_height)
solid_body = solid_body - slot

part = solid_body
part.name = "cylindrical_shell_with_tab"
export_step(part, "output.step")