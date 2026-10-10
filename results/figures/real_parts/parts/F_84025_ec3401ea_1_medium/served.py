from build123d import *

# ---- Dimensions (mm) ----
flange_diameter = 80.0          # Ø80 flange
flange_thickness = 13.8         # flange thickness
flange_flat_width = 60.7        # 60.7 A/F
body_diameter = 49.7            # Ø49.7 body
body_height = 44.1              # body height above flange
total_height = 60.7             # overall height
bore_diameter = 27.6            # Ø27.6 THRU
hole_diameter = 6.9             # Ø6.9 holes
hole_count = 6
hole_circle_diameter = 65.0     # bolt circle of the 6 holes
top_fillet_radius = 2.8         # R2.8 on top edges

# ---- Build the part ----
with BuildPart() as p:
    # Flange: Ø80 disc with two flats 60.7 apart, 13.8 thick
    with BuildSketch(Plane.XY) as flange_sk:
        Circle(flange_diameter / 2)
        Rectangle(flange_flat_width, flange_diameter, mode=Mode.INTERSECT)
    extrude(amount=flange_thickness)

    # Body: Ø49.7 cylinder standing on the flange
    with BuildSketch(Plane.XY.offset(flange_thickness)) as body_sk:
        Circle(body_diameter / 2)
    extrude(amount=body_height)

    # Central through bore Ø27.6
    with BuildSketch(Plane.XY) as bore_sk:
        Circle(bore_diameter / 2)
    extrude(amount=total_height, mode=Mode.SUBTRACT)

    # 6x Ø6.9 holes on a bolt circle, through the flange
    with BuildSketch(Plane.XY) as holes_sk:
        with PolarLocations(hole_circle_diameter / 2, hole_count):
            Circle(hole_diameter / 2)
    extrude(amount=flange_thickness, mode=Mode.SUBTRACT)

    # R2.8 fillet on the top outer edge and top bore edge
    top_face = p.part.faces().sort_by(Axis.Z)[-1]
    fillet(top_face.edges(), radius=top_fillet_radius)

part = p.part
part.name = "flanged_body_with_bore_and_holes"
export_step(part, "output.step")