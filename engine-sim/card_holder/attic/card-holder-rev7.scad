include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>

$fn=37;

difference_fudge = 0.1;
extrusion_fudge = 0.1;

acrylic_thickness = 3.25;

mag_diam = 8 + extrusion_fudge * 2;
mag_thickness = 3 - extrusion_fudge;

frame_xside_width = 12;
frame_yside_width = 14;
frame_extra_thickness = 3;
mag_frame_offset = 4;
acrylic_depth = 2;

frame_overlap = 2;

card_width = 54;
card_height = 81;
card_thickness = acrylic_thickness;

frame_width = card_width + (frame_xside_width - frame_overlap) * 2;
frame_height = card_height+ (frame_yside_width - frame_overlap) * 2;
frame_depth = frame_extra_thickness + acrylic_thickness;
corner_fillet = 2;

reed_diam = 2.2;
reed_length = 14;
reed_leg_length = 12;
bend_allowance = 2;
conn_allowance = 5;

thru_hole_diam = 1.5;

resistor_diam = 2.5;
resistor_length = 7;
resistor_leg_length = 24;

res_channel_length = conn_allowance * 2 + resistor_length;
thru_hole_offset = thru_hole_diam / 2 + bend_allowance / 2;

wire_diam = 1;

plate_thickness = frame_depth;
plate_length = 50;
plate_offset = 10;

zflip()
{
    frame();

    translate([frame_width, 0, 0])
    snap();

    translate([-frame_width * 1.25, 0, 0])
    back_frame();
}

module frame()
{
    spread_height = frame_height - mag_diam - mag_frame_offset;
    spread_width = frame_width - mag_diam - mag_frame_offset;

    difference()
    {
        color("blue")
        cuboid([frame_width, frame_height, frame_depth], fillet=corner_fillet);
        
        color("magenta")
        cuboid([
            card_width - frame_overlap * 2, 
            card_height - frame_overlap * 2, 
            frame_depth * 2
        ], fillet=corner_fillet);
        
        color("yellow")
        translate([0, 0, -frame_depth + frame_depth / 2 - acrylic_depth])
        cuboid([
            card_width, 
            card_height, 
            frame_depth * 2
        ]);
       
        color("silver")
        translate([0, 0, -(frame_depth - mag_thickness + difference_fudge) / 2])
        {
            translate([0, spread_height / 2, 0])
            xspread(spacing=spread_width, l=spread_width) {
                cyl(l=mag_thickness +  + difference_fudge, d=mag_diam);
            }
            
            translate([0, -spread_height / 2, 0])
            xspread(spacing=spread_width / 6, l=spread_width) {
                cyl(l=mag_thickness + difference_fudge, d=mag_diam);
            }
           
        }
    }
}

module snap()
{
    intersection()
    {
        difference() {
            color("blue")
            cuboid([frame_width, frame_height, frame_depth], fillet=corner_fillet);
            
            color("magenta")
            cuboid([
                card_width - frame_overlap * 2, 
                card_height - frame_overlap * 2, 
                frame_depth * 2
            ], fillet=corner_fillet);
        }
        
        color("yellow")
        translate([0, 0, 
            -frame_depth + frame_depth / 2 - acrylic_depth - acrylic_thickness])
        cuboid([
            card_width, 
            card_height, 
            frame_depth * 2
        ]);
        
    }
}

mag_projection_depth = (3/16) * 25.4;
mag_projection_collar_thickness = mag_frame_offset;

module back_frame()
{
    spread_height = frame_height - mag_diam - mag_frame_offset;
    spread_width = frame_width - mag_diam - mag_frame_offset;
    
    switch_plate_width = spread_width / 6 * 5;

    //bottom_half(z=-frame_depth / 2 + mag_thickness + acrylic_depth, s=frame_height * 1.5)
    difference()
    {
        union()
        {
            difference()
            {
                color("blue")
                cuboid(
                    [frame_width, frame_height, frame_depth], 
                    fillet=corner_fillet, edges=EDGES_Z_ALL);
                
                color("yellow")
                cuboid([
                    card_width, 
                    card_height, 
                    frame_depth * 2
                ]);
               
                translate([0, -spread_height / 2, 0])
                cuboid([
                    switch_plate_width, 
                    frame_height / 2, 
                    frame_depth * 2
                ]);
            }
            
            translate([0, -spread_height / 2, 0])
            switch_plate(switch_plate_width, spread_width);
            
            color("red")
            translate([
                0, 0, 
                -(frame_depth + mag_projection_depth - difference_fudge) / 2
            ])
            {
                translate([0, spread_height / 2, 0])
                xspread(spacing=spread_width, l=spread_width) {
                    cyl(
                        l=mag_projection_depth + difference_fudge, 
                        d=mag_diam + mag_projection_collar_thickness
                    );
                }
                
                translate([0, -spread_height / 2, 0])
                xspread(spacing=spread_width, l=spread_width) {
                    cyl(
                        l=mag_projection_depth + difference_fudge, 
                        d=mag_diam + mag_projection_collar_thickness
                    );
                }
            }

        }
        
        color("silver")
        translate([
            0, 0, 
            (-frame_depth - mag_projection_depth * 2
                + mag_thickness - difference_fudge
             ) / 2
        ])
        {
            translate([0, spread_height / 2, 0])
            xspread(spacing=spread_width, l=spread_width) {
                cyl(l=mag_thickness + difference_fudge, d=mag_diam);
                
                cyl(l=99, d=thru_hole_diam);
            }
            
            translate([0, -spread_height / 2, 0])
            xspread(spacing=spread_width, l=spread_width) {
                cyl(l=mag_thickness + difference_fudge, d=mag_diam);

                cyl(l=99, d=thru_hole_diam);
            }
        }
    }
}

module switch_plate(switch_plate_width, spread_width)
{
    translate([0, -reed_length / 2, -frame_depth / 2 + plate_thickness / 2])
    difference()
    {
        translate([0, -plate_offset, 0])
        cuboid([
            switch_plate_width + frame_xside_width / 2, 
            plate_length, 
            plate_thickness
        ], fillet=corner_fillet, edges=EDGES_Z_ALL);
    
        xspread(spacing=spread_width / 6, l=spread_width * 2 / 3) {
            switch_assy(spread_width / 6);
        }
                
        * translate([
            -spread_width /3 + spread_width / 12, 
            0,  
            plate_thickness / 2
        ])
        {
            color("lightblue")
            ycyl(l = resistor_length, d = resistor_diam);

            color("silver")
            ycyl(l = res_channel_length, d = wire_diam);
        
        }
        
        translate([
            -spread_width /3 + spread_width / 12,
            reed_length / 2 + thru_hole_offset 
                - conn_allowance * 2,  
            plate_thickness / 2
        ])
        {
            color("silver")
            ycyl(l = conn_allowance, d = wire_diam, align=V_BACK);        
            color("silver")
            translate([wire_diam / 2, 0, 0])
            xcyl(l=99, d=wire_diam, align=V_LEFT);
            
            color("lightblue")
            translate([-conn_allowance, 0, 0])
            xcyl(l = resistor_length, d = resistor_diam);

        }


        color("silver")
        translate([
            spread_width /3 - spread_width / 12,
            reed_length / 2 + thru_hole_offset 
                - conn_allowance * 2,  
            plate_thickness / 2
        ])
        {
            ycyl(l = conn_allowance, d = wire_diam, align=V_BACK);        
            translate([-wire_diam / 2, 0, 0])
            xcyl(l=99, d=wire_diam, align=V_RIGHT);
        }

    }
}

module switch_assy(spread_width)
{
    // Front side (reed switches)
    translate([0, 0, -plate_thickness / 2])
    {
        color("#aaffaa")
        cuboid([reed_diam, reed_length + thru_hole_offset * 2, reed_diam]);

        translate([0, 0, reed_diam / 2])
        ycyl(l=reed_length + thru_hole_offset * 2, d=reed_diam);
    }
    
    // Back side (everything else)
    translate([0, 0, plate_thickness / 2])
    {
        // Top components (ground/analog line)                        
        translate([0, reed_length / 2 + thru_hole_offset, 0])
        {
            color("silver")
            zcyl(l=plate_thickness * 6, d=thru_hole_diam);

            color("silver")
            translate([0, -conn_allowance / 2, 0])
            ycyl(l = conn_allowance, d = wire_diam);
            
            color("silver")
            translate([0, -conn_allowance, 0])
            xcyl(l=spread_width * 1.1, d=wire_diam);
        }

        // Bottom components (resistors)
        translate([0, -reed_length / 2 - thru_hole_offset, 0])
        {
            color("silver")
            zcyl(l=plate_thickness * 6, d=thru_hole_diam);
            
            translate([0, -res_channel_length / 2, 0])
            {
                color("lightblue")
                ycyl(l = resistor_length, d = resistor_diam);

                color("silver")
                ycyl(l = res_channel_length, d = wire_diam);
            
            }
            
            color("silver")
            translate([0, -res_channel_length, 0])
            xcyl(l=spread_width * 2, d=wire_diam);
        }
    }
}

module card()
{
    color("red")
    cuboid([card_width, card_height, card_thickness]);
}
