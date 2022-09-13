include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>

$fn=37;

split_model = true;
laser_projection = true;

difference_fudge = 0.1;
extrusion_fudge = 0.1;

acrylic_thickness = 3.25;

corner_fillet = 2;

card_width = 54;
card_height = 81;
card_thickness = 4;
card_slot_play = 2;

strip_width = 12;
strip_length = card_width;
strip_height = 1;
led_width = 5.2;
led_height = 2;

led_wire_allotment = 5;

back_wall_thickness = 5.5;
back_plate_thickness = 3;
front_wall_thickness = 3;
side_wall_thickness = 6;
base_height = 10;
base_thickness = 13;

total_width = strip_length 
    + (led_wire_allotment + side_wall_thickness) * 2;

card_support_width = 2;
card_support_play = 2;

reader_thickness = 1;
reader_width = 40;
reader_height = 60;
reader_blob_width = 4.5;
reader_blob_height = 13;
reader_blob_thickness = 5;
reader_slot_play = 1;

reader_post_drop_top = 6.5;
reader_post_width_top = 25;
reader_post_width_bottom = 34.5;
reader_post_drop_bottom = 16;
rfid_post_diam = 2.75;
rfid_post_height = 4;
rfid_wiring_allowance = 7;

// M3 hex-head screws
mounting_screw_diam = 3.1;
mounting_screw_length = 20;
mounting_screw_head_diam = 5.7;
actual_mounting_screw_head_depth = 3;

// Make the 'screw head' a bit deeper so that the screws will be
// inset on the surface
mounting_screw_head_depth = actual_mounting_screw_head_depth + 0.5;

led_offset_y = -(strip_width + back_wall_thickness) / 2;
strip_box_height = strip_height + led_height + acrylic_thickness;
slot_thickness = strip_width 
    + front_wall_thickness + back_wall_thickness;
strip_cutout_thickness = strip_width 
    + back_wall_thickness + back_plate_thickness;

if(split_model) 
{
    if(laser_projection) {
        projection()
        bottom_split();
    } else {
        top_split();
        bottom_split();
    }
}
else 
{
    card_holder();
}

module top_split()
{
    rotate([-90, 0, 0])
    {
        translate([-50, 0, 0])
        {
            rotate([0, 0, 180])
            union()
            {
                front_half(y = -10, s=200)
                card_holder();

                // alignment pins
                translate([
                    -total_width / 2 + side_wall_thickness, 
                    -10, 
                    card_height / 2
                ])
                ycyl(l=rfid_post_height * 2, d=rfid_post_diam - extrusion_fudge);

                translate([
                    total_width / 2 - side_wall_thickness, 
                    -10, 
                    card_height / 2
                ])
                ycyl(l=rfid_post_height * 2, d=rfid_post_diam - extrusion_fudge);
            }
        }
    }
}

module bottom_split()
{
    
    rotate([-90, 0, 0])
    {
        translate([50, 0, 0])
        {
            difference()
            {
                back_half(y = -10, s=200)
                card_holder();

                // alignment holes
                translate([
                    -total_width / 2 + side_wall_thickness, 
                    -10, 
                    card_height / 2
                ])
                ycyl(l=rfid_post_height * 2, d=rfid_post_diam + extrusion_fudge);

                translate([
                    total_width / 2 - side_wall_thickness, 
                    -10, 
                    card_height / 2
                ])
                ycyl(l=rfid_post_height * 2, d=rfid_post_diam + extrusion_fudge);

                // mounting screw holes
                translate([
                    -total_width / 2 + side_wall_thickness, 
                    -10 + mounting_screw_head_depth - extrusion_fudge,
                    card_height / 1.5
                ])
                mounting_screw();
                
                translate([
                    total_width / 2 - side_wall_thickness, 
                    -10 + mounting_screw_head_depth - extrusion_fudge,
                    card_height / 1.5
                ])
                mounting_screw();
            }
        }
    }
}

module mounting_screw()
{
    color("#444444")
    union()
    {
        translate([0, mounting_screw_length / 2 - difference_fudge / 2, 0])
        ycyl(
            l=mounting_screw_length + difference_fudge, 
            d=mounting_screw_diam);
        
        translate([0, -mounting_screw_head_depth / 2 + difference_fudge / 2, 0])
        ycyl(
            l=mounting_screw_head_depth + difference_fudge, 
            d=mounting_screw_head_diam);
    }
}


* card();
* rfid_reader();
* led_strip();

module card_holder()
{
    union()
    {
        card_slot();
        led_base();
    }
}

module card_slot()
{
    card_cutout_bottom_thickness = card_thickness + card_support_play;
    card_cutout_top_thickness = card_thickness * 2.5;
    card_cutout_height = card_height - strip_box_height;

    translate([
        0,
        -slot_thickness / 2,
        card_height / 2]
    )
    // left_half(s = 200)
    // bottom_half(z=-20)
    union()
    {
        // Slot body
        difference()
        {
            cuboid(
                [
                    total_width,
                    slot_thickness, 
                    card_height + extrusion_fudge
                ], 
                fillet=corner_fillet,
                edges=EDGES_Y_TOP + EDGE_TOP_FR + EDGES_Z_FR
            );
        
            // This is the cutout to make the card visible, it is inset 
            // from the card edges by card_support_width on either side 
            // so the card won't fall out
            translate([
                0, 
                -slot_thickness, 
                card_support_width + strip_box_height
            ])
            cuboid([
                card_width - card_support_width * 2, 
                slot_thickness * 2, 
                card_height
            ]);
            
            // This is the cutout for the RFID card
            translate([
                0, 
                slot_thickness, 
                -(card_height - reader_height) / 2 + strip_box_height
            ])
            cuboid([
                reader_width + reader_slot_play, 
                slot_thickness * 2, 
                reader_height + reader_slot_play
            ]);
            
            // This is the cutout that holds the LED strip, it is open to the back
            // for wiring access through the board
            translate([
                0, 
                slot_thickness / 2 + led_offset_y + back_wall_thickness / 2, 
                -(card_height - strip_box_height) / 2 - difference_fudge / 2
            ])
            cuboid([
                strip_length + led_wire_allotment * 2, 
                strip_cutout_thickness, 
                strip_box_height + difference_fudge
            ]);
            
            card_slot_cutout(
                card_cutout_top_thickness, 
                card_cutout_bottom_thickness,
                card_cutout_height,
                strip_box_height
            );
        }

        translate([
            0, 
            (slot_thickness + back_plate_thickness) / 2, 
            -base_height / 2
        ])
        back_plate();
    }
   
}

module back_plate()
{
    back_plate_height = card_height + base_height;
    // Back plate
    difference()
    {
        union()
        {
            cuboid(
                [
                    total_width,
                    back_plate_thickness, 
                    back_plate_height
                ], 
                fillet=corner_fillet,
                edges=EDGES_Y_TOP
            );

            translate([
                -reader_post_width_bottom / 2, 
                -(back_plate_thickness + rfid_post_height) / 2,
                -back_plate_height / 2 
                    + base_height + strip_box_height + reader_post_drop_bottom
            
            ])
            ycyl(l=rfid_post_height, d=rfid_post_diam);
            
            translate([
                reader_post_width_bottom / 2, 
                -(back_plate_thickness + rfid_post_height) / 2,
                -back_plate_height / 2 
                    + base_height + strip_box_height + reader_post_drop_bottom
            ])
            ycyl(l=rfid_post_height, d=rfid_post_diam);
            
            translate([
                -reader_post_width_top / 2, 
                -(back_plate_thickness + rfid_post_height) / 2,
                -back_plate_height / 2 
                    + base_height + strip_box_height + reader_height
                    - reader_post_drop_top
            ])
            ycyl(l=rfid_post_height, d=rfid_post_diam);
            
            translate([
                reader_post_width_top / 2, 
                -(back_plate_thickness + rfid_post_height) / 2,
                -back_plate_height / 2 
                    + base_height + strip_box_height + reader_height
                    - reader_post_drop_top
            ])
            ycyl(l=rfid_post_height, d=rfid_post_diam);
        }
        
        // This is the cutout for the RFID card wiring
        translate([
            0, 
            0, 
            -back_plate_height / 2 
                + base_height + strip_box_height +  rfid_wiring_allowance / 2
                - difference_fudge / 2
        ])
        cuboid([
            reader_width + reader_slot_play, 
            back_plate_thickness * 2, 
            rfid_wiring_allowance + difference_fudge
        ]);
        
        // This is the cutout that holds the LED strip, it is open to the back
        // for wiring access through the board
        translate([
            0, 
            slot_thickness / 2 + led_offset_y + back_wall_thickness / 2, 
            -back_plate_height / 2 
                + base_height + strip_box_height / 2
                - difference_fudge / 2
        ])
        cuboid([
            strip_length + led_wire_allotment * 2, 
            strip_cutout_thickness, 
            strip_box_height + difference_fudge
        ]);
    }
}

module rfid_reader()
{
    translate([
        0, 
        -reader_thickness / 2, 
        reader_height / 2 + strip_box_height
    ])
    {
        color("silver")
        translate([
            -(reader_width - reader_blob_width) / 2, 
            -reader_blob_thickness / 2,
            -(reader_height - reader_blob_height) / 2
        ])
        cuboid([reader_blob_width, reader_blob_thickness, reader_blob_height]);
        
        difference()
        {
            color("#0000aa")
            cuboid([reader_width, reader_thickness, reader_height]);
                
            color("red")
            translate([
                -reader_post_width_bottom / 2, 
                0,
                -reader_height / 2 + reader_post_drop_bottom
            ])
            ycyl(l=reader_thickness * 2, d=rfid_post_diam);
            
            color("red")
            translate([
                reader_post_width_bottom / 2, 
                0,
                -reader_height / 2 + reader_post_drop_bottom
            ])
            ycyl(l=reader_thickness * 2, d=rfid_post_diam);
            
            color("red")
            translate([
                -reader_post_width_top / 2, 
                0,
                reader_height / 2 - reader_post_drop_top
            ])
            ycyl(l=reader_thickness * 2, d=rfid_post_diam);
            
            color("red")
            translate([
                reader_post_width_top / 2, 
                0,
                reader_height / 2 - reader_post_drop_top
            ])
            ycyl(l=reader_thickness * 2, d=rfid_post_diam);
        }
    }   
}

module card()
{
    color("red", 0.25)
    translate([
        0, 
        led_offset_y, 
        card_height/ 2 + strip_box_height
    ])
    cuboid([card_width, card_thickness, card_height]);
}

module card_slot_cutout(top_slot_thickness, bottom_slot_thickness, slot_height,
    strip_box_height)
{
    // Card slot cutout - wedge
    translate([
        0, 
        (card_thickness - card_support_play) / 2, 
        -(slot_height - strip_box_height) / 2 - difference_fudge / 2
    ])
    prismoid(
        size1=[
            card_width + card_slot_play,
            bottom_slot_thickness
        ], 
        size2=[
            card_width + card_slot_play,
            top_slot_thickness
        ], 
        h=slot_height + difference_fudge, 
        shift=[
            0, 
            -(top_slot_thickness - bottom_slot_thickness) / 2
        ]
    );
}

module led_base()
{
    union()
    {
        translate([0, -(corner_fillet * 1.5) / 2, -base_height / 2])
        cuboid([total_width, corner_fillet * 1.5, base_height]);
        
        translate([0, -base_thickness / 2, -base_height])
        rounded_prismoid(
            size1=[
                total_width,
                base_thickness
            ], 
            size2=[
                total_width,
                slot_thickness
            ], 
            h=base_height,
            r=corner_fillet,
            shift=[
                0, 
                -(slot_thickness - base_thickness) / 2
            ]
        );
    }
}

module led_strip()
{
    translate([0, led_offset_y, 0])
    {
        color("black")
        upcube([strip_length, strip_width, strip_height]);
        
        color("white")
        translate([0, 0, strip_height])
        upcube([strip_length, led_width, led_height]);

        translate([0, 0, strip_height + led_height])
        color("#aaaaaa", 0.3)
        upcube([strip_length, strip_width, acrylic_thickness]);
    }
}