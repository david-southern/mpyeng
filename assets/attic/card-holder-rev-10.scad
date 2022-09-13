include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>

$fn=37;

laser_cut = false;
show_plate = true;

difference_fudge = 0.1;
extrusion_fudge = 0.1;
print_layer_height = 0.15;

acrylic_thickness = 3.25;

mag_diam = 8 + extrusion_fudge * 2;
mag_thickness = 3;

min_frame_thickness = max(2, mag_thickness);

frame_xside_width = 12;
frame_yside_width = 14;
mag_frame_offset = 4;

frame_overlap = 2;

card_width = 54;
card_height = 81;
card_thickness = acrylic_thickness;

frame_width = card_width + (frame_xside_width - frame_overlap) * 2;
frame_height = card_height+ (frame_yside_width - frame_overlap) * 2;
frame_depth = 4.25;
corner_fillet = 2;

reed_diam = 2.2;
reed_length = 14;
reed_leg_length = 12;

min_reed_sep = 15;

bend_allowance = 4;
conn_allowance = 4;

thru_hole_diam = 1.5;

resistor_diam = 2.5;
resistor_length = 7;
resistor_leg_length = 24;

res_channel_length = conn_allowance * 2 + resistor_length;
thru_hole_offset = thru_hole_diam / 2 + bend_allowance / 2;

wire_diam = 1;

plate_thickness = frame_depth;
plate_length = 30;
plate_offset = 2;

mag_projection_depth = (3/16) * 25.4;
mag_projection_collar_thickness = mag_frame_offset;

strip_width = 12.5;
strip_height = 1.7;
led_width = 5.2;
led_height = 2.1;

card_frame_depth = strip_width 
    + min_frame_thickness * 2 
    + print_layer_height * 6.5;

mag_switch_pivot_len = mag_diam * 3;
mag_switch_wall = 2;

module mag_switch()
{
    switch_width = mag_diam + mag_switch_wall * 2;
    switch_len = mag_switch_pivot_len + mag_switch_wall * 2;
    switch_thickness = mag_thickness + mag_switch_wall;
    
    difference()
    {
        cuboid([switch_width, switch_len, switch_thickness],
            fillet=switch_width / 2, edges=EDGES_Z_ALL);
        
        color("silver")
        translate([0, 0, switch_thickness / 2])
        cyl(l=mag_thickness + difference_fudge, d=mag_diam);
    }
}

if(show_plate) {
    if(laser_cut) 
    {
        projection(cut = true)
        translate([0, 0, frame_depth / 2 + 1])
        back_frame();    
    }
    else     
    {
        bottom_half(s=150)
        card_frame();


        
        zflip()
        {
            translate([frame_width * 1.25, 0, 0])
            top_half(s=150)
            card_frame();
            
            translate([-frame_width * 1.25, 0, 0])
            back_frame();
        }
    }
}

module led_strip(strip_length)
{
    translate([0, 0, -led_height])
    {
        color("white")
        upcube([strip_length, led_width, led_height]);

        color("black")
        upcube([strip_length, strip_width, strip_height]);
    }
}

module card_frame()
{
    spread_height = frame_height - mag_diam - mag_frame_offset;
    spread_width = frame_width - mag_diam - mag_frame_offset;

    difference()
    {
        color("blue")
        cuboid([frame_width, frame_height, card_frame_depth], fillet=corner_fillet);
        
        color("magenta")
        cuboid([
            card_width - frame_overlap * 2, 
            card_height - frame_overlap * 2, 
            card_frame_depth * 2
        ], fillet=corner_fillet);
        
        color("yellow")
        translate([0, 0, card_frame_depth / 2 -
            min_frame_thickness - strip_width / 2 + acrylic_thickness / 2])
        downcube([
            card_width,
            card_height, 
            acrylic_thickness
        ]);

        // Channels for the LED strip
        translate([card_width / 2 - difference_fudge / 2, 0, 0])
        rotate([-90, 0, 90])
        led_strip(spread_height);
        
        translate([-card_width / 2 + difference_fudge / 2, 0, 0])
        rotate([90, 0, 90])
        led_strip(spread_height);        

        // Mags along the left and right sides of the frame
        translate([spread_width / 2, 0, 
            -(card_frame_depth - mag_thickness + difference_fudge) / 2])
        yspread(spacing=spread_height / 4, l=spread_height, n = 3) {
            cyl(l=mag_thickness +  + difference_fudge, d=mag_diam);            
        } 
        
        translate([-spread_width / 2, 0, 
            -(card_frame_depth - mag_thickness + difference_fudge) / 2])
        yspread(spacing=spread_height / 3, l=spread_height, n = 2) {
            cyl(l=mag_thickness +  + difference_fudge, d=mag_diam);
        }

        // Mounting mags and LED channels
        color("silver")
        yspread(spacing=spread_height, l=spread_height) {
            cuboid([spread_width, led_height, strip_width]);
            xspread(spacing=spread_width, l=spread_width) {
                downcyl(l=card_frame_depth, d=thru_hole_diam);
                translate([0, 0, 
                    -(card_frame_depth - mag_thickness + difference_fudge) / 2])
                {
                    cyl(l=mag_thickness + difference_fudge, d=mag_diam);
                }
            }
        }
    }
}

module back_frame()
{
    spread_height = frame_height - mag_diam - mag_frame_offset;
    spread_width = frame_width - mag_diam - mag_frame_offset;

    echo(spread_width=spread_width);
    echo(spread_height=spread_height);
    echo(collar_diam=mag_diam + mag_projection_collar_thickness);
    
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
               
                translate([-spread_width / 2, 0, 0])
                cuboid([
                    plate_length,
                    spread_height - conn_allowance * 2, 
                    frame_depth * 2
                ]);
               
                translate([spread_width / 2, 0, 0])
                cuboid([
                    plate_length,
                    spread_height - conn_allowance * 2, 
                    frame_depth * 2
                ]);  
            }
            
            translate([-spread_width / 2, 0, 0])
            rotate([0, 0, 90])
            switch_plate(spread_height, 3);
            
            translate([spread_width / 2, 0, 0])
            rotate([0, 0, -90])
            switch_plate(spread_height, 2);
            
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
        
        // Bottom connection channel
        color("silver")                        
        translate([plate_offset / 4, -spread_height / 2 + conn_allowance, frame_depth / 2]) 
        {
            ycyl(l = 99, d = wire_diam, align=V_FRONT);   
            
            translate([-wire_diam / 2, 0, 0])
            xcyl(l=plate_length + conn_allowance + plate_offset / 2, d=wire_diam);
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
        
    
        // Top connection channel
        translate([plate_offset / 4, spread_height / 2 - conn_allowance, 
            frame_depth / 2]) 
        {
            color("silver")                        
            translate([resistor_length / 2 + conn_allowance, 0, 0])
            ycyl(l = conn_allowance, d = wire_diam, align=V_BACK);   
            
            translate([0, conn_allowance, 0]) {
                color("lightblue")
                xcyl(l = resistor_length, d = resistor_diam);   
                
                color("silver")                        
                xcyl(l = resistor_length + conn_allowance * 2 + wire_diam / 2, d = wire_diam);   
            }
            
            color("silver")                        
            translate([-resistor_length / 2 - conn_allowance, conn_allowance, 0])
            ycyl(l = 99, d = wire_diam, align=V_BACK);   
            
            color("silver")                        
            translate([-wire_diam / 2, 0, 0])
            xcyl(l=plate_length + conn_allowance + plate_offset / 2, d=wire_diam);
        }

        color("black")                        
        translate([
            resistor_length / 2 + conn_allowance + wire_diam * 2,
            spread_height / 2, frame_depth / 2])
        linear_extrude(height = 2, center = true)
        text("GND", font = "Arial", size=frame_yside_width / 3, 
            halign="left", valign="center");
         
        
        color("green")                        
        translate([wire_diam * 4, -spread_height / 2 - wire_diam, frame_depth / 2])
        {
            linear_extrude(height = 2, center = true)
            text("Aout", font = "Arial", size=frame_yside_width / 3, 
                halign="left", valign="center");        
        }
    
        color("red")                        
        translate([
            spread_width / 2 - conn_allowance, 
            -spread_height / 2 + mag_diam / 1.5, frame_depth / 2])
        {
            linear_extrude(height = 2, center = true)
            text("5V", font = "Arial", size=frame_yside_width / 3, 
                halign="center", valign="center");        
        }
    
        color("red")                        
        translate([-spread_width / 2 + conn_allowance, 
            -spread_height / 2 + mag_diam / 1.5, frame_depth / 2])
        {
            linear_extrude(height = 2, center = true)
            text("5V", font = "Arial", size=frame_yside_width / 3, 
                halign="center", valign="center");        
        }
        
        /*
  * R1: 10Kohm
  * R2: 4.7Kohm
  * R3: 2.2Kohm
  * R4: 1Kohm
  * R5: 470ohm
        */
        color("lightblue")                        
        translate([-spread_width / 2 - 2.5, -spread_height / 2 + 29, frame_depth / 2])
        {
            linear_extrude(height = 2, center = true)
            text("470", font = "Arial", size=4, 
                halign="center", valign="center");        
        }        
        
        color("lightblue")                        
        translate([-spread_width / 2 - 2.5, -spread_height / 2 + 52, frame_depth / 2])
        {
            linear_extrude(height = 2, center = true)
            text("2.2K", font = "Arial", size=4, 
                halign="center", valign="center");        
        }        
        
        color("lightblue")                        
        translate([-spread_width / 2 - 2.5, -spread_height / 2 + 75, frame_depth / 2])
        {
            linear_extrude(height = 2, center = true)
            text("10K", font = "Arial", size=4, 
                halign="center", valign="center");        
        }        

        color("lightblue")                        
        translate([spread_width / 2 + 1.5, -spread_height / 2 + 36, frame_depth / 2])
        {
            linear_extrude(height = 2, center = true)
            text("1K", font = "Arial", size=4, 
                halign="center", valign="center");        
        }        
        

        color("lightblue")                        
        translate([+spread_width / 2 + 2.5, -spread_height / 2 + 67, frame_depth / 2])
        {
            linear_extrude(height = 2, center = true)
            text("4.7K", font = "Arial", size=4, 
                halign="center", valign="center");        
        }        
        
        
    }
}

module switch_plate(switch_plate_width, switch_count)
{
    translate([0, 0, -frame_depth / 2 + plate_thickness / 2])
    difference()
    {
        translate([0, -plate_offset, 0])
        cuboid([
            switch_plate_width + frame_xside_width / 2, 
            plate_length, 
            plate_thickness
        ], fillet=corner_fillet, edges=EDGES_Z_ALL);
    
        xspread(spacing=switch_plate_width / (switch_count + 1), 
            l=switch_plate_width, n = switch_count) {
            switch_assy(switch_plate_width / (switch_count + 1));
        }        
    }
}

module switch_assy(assy_width)
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
        translate([0, -reed_length / 2 - thru_hole_offset, 0])
        {
            color("silver")
            zcyl(l=plate_thickness * 6, d=thru_hole_diam);

            color("silver")
            translate([0, -conn_allowance / 2, 0])
            ycyl(l = conn_allowance, d = wire_diam);
            
            color("silver")
            translate([0, -conn_allowance, 0])
            xcyl(l=assy_width * 2.5, d=wire_diam);
        }

        // Bottom components (resistors)
        translate([0, reed_length / 2 + thru_hole_offset, 0])
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
            xcyl(l=assy_width * 1.2, d=wire_diam);
        }
    }
}

module card()
{
    color("red")
    cuboid([card_width, card_height, card_thickness]);
}
