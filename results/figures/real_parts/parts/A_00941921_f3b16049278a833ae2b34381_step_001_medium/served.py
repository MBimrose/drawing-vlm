from build123d import *

# --- dimensions from the drawing ---
overall = 80.0                 # overall width / height of the cross
thickness = 5.7
outer_dia = 57.1               # outer diameter of the ring
inner_dia = 41.9               # inner diameter (through bore)
hole_dia = 5.4                 # four mounting holes
hole_pitch_radius = 28.55      # hole pattern radius (on the arm centerlines)
chamfer_size = 1.9

# --- cross profile in the XZ plane, extruded along Y ---
with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        Circle(outer_dia / 2)                      # central ring
        Rectangle(overall, thickness)             # horizontal arm
        Rectangle(thickness, overall)             # vertical arm
    extrude(amount=thickness)

solid_body = p.part

# --- central through bore ---
solid_body = solid_body - Rot(90, 0, 0) * Cylinder(inner_dia / 2, thickness * 2)

# --- four mounting holes, one in each arm ---
for x, z in [(hole_pitch_radius, 0), (-hole_pitch_radius, 0),
             (0, hole_pitch_radius), (0, -hole_pitch_radius)]:
    solid_body = solid_body - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(hole_dia / 2, thickness * 2)

# --- chamfer the outer perimeter edges of the cross profile ---
solid_body = chamfer(solid_body.edges().filter_by(Axis.Y), chamfer_size)

part = solid_body
part.name = "cross_plate"
export_step(part, "output.step")