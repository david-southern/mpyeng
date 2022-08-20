include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>

$fn=37;

laser_cut = false;

difference_fudge = 0.1;
extrusion_fudge = 0.1;

acrylic_thickness = 3.25;

corner_fillet = 2;

card_width = 54;
card_height = 81;
card_thickness = 4;
card_slot_play_x = 2;
card_slot_play_y = 2;
card_slot_play_z = 12;

strip_width = 12;
strip_length = card_width;
strip_height = 1;
led_width = 5.2;
led_height = 2;

led_wire_allotment = 7;

back_wall_thickness = 5.5;
back_plate_thickness = 3;
front_wall_thickness = 4;
side_wall_thickness = 6;
base_height = 10;
base_thickness = 13;

card_support_width = 2;

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

led_offset_y = -(strip_width + back_wall_thickness) / 2;
strip_box_height = strip_height + led_height + acrylic_thickness;

slot_width = card_width + card_slot_play_x;
slot_height = card_height;
slot_thickness = card_thickness + card_slot_play_y;

holder_thickness = slot_thickness + front_wall_thickness;
holder_width = strip_length + (led_wire_allotment + side_wall_thickness / 2) * 2;
holder_height = card_height + strip_box_height + side_wall_thickness 
    - card_slot_play_z;
    

card_y_offset = -card_thickness / 2;

* card();
* rfid_reader();
* translate([0, 0, -card_height / 2]) led_strip();

if(laser_cut) {
    projection(cut = true) 
    {
        rotate([-90, 0, 0])
        {
            difference()
            {
                holder_body();
                alignment_pins();
                acrylic_slot();
                led_slot();
            }
        }
    }
}
else 
{
    card_holder();
}

module card_holder()
{
    union()
    {
        difference()
        {
            holder_body();
            card_slot();
            card_cutout();
            acrylic_slot();
            led_slot();
        }
        alignment_pins();
    }
}

module alignment_pins()
{
    alignment_width = holder_width / 2 - (holder_width - slot_width) / 4;
    echo(alignment_width=alignment_width * 2);
    echo(alignment_diam=rfid_post_diam);
    
    // alignment pins
    color("magenta")
    translate([-alignment_width, 0, 0])
    ycyl(l=rfid_post_height * 2, d=rfid_post_diam - extrusion_fudge);

    color("magenta")
    translate([alignment_width, 0, 0])
    ycyl(l=rfid_post_height * 2, d=rfid_post_diam - extrusion_fudge);
}

module holder_body()
{
    translate([0, 
        -holder_thickness / 2, 
        -(strip_box_height + side_wall_thickness)
    ])
    cuboid(
        [
            holder_width,
            holder_thickness, 
            holder_height
        ], 
        fillet=corner_fillet
        , edges=EDGES_FRONT + EDGES_Y_ALL
    );
}

module card_slot()
{
    color("magenta")
    translate([
        0, 
        -slot_thickness / 2 + difference_fudge / 2,
        -difference_fudge / 2
    ])
        cuboid(
        [
            slot_width,
            slot_thickness + difference_fudge,
            slot_height + difference_fudge
        ]
    );
}


module card_cutout()
{
    // This is the cutout to make the card visible, it is inset 
    // from the card edges by card_support_width on either side 
    // so the card won't fall out
    
    color("magenta")
    translate([
        0,
        -holder_thickness / 2,
        -difference_fudge / 2
    ])
    cuboid(
        [
            card_width - card_support_width * 2, 
            holder_thickness * 2, 
            card_height
        ], 
        fillet=corner_fillet
    );
}


module acrylic_slot()
{
    // This is the cutout that holds the LED acrylic, it is open to the back
    // for wiring access through the board
    
    color("magenta")
    translate([
        0, 
        card_y_offset, 
        -card_height / 2 - acrylic_thickness / 2 + difference_fudge / 2
    ])
    cuboid([
        strip_length + led_wire_allotment * 2, 
        strip_width, 
        acrylic_thickness + difference_fudge
    ]);
}

module led_slot()
{
    // This is the cutout that holds the LED strip, it is open to the back
    // for wiring access through the board
    
    union()
    {
        color("magenta")
        translate([
            0, 
            card_y_offset, 
            -card_height / 2 - acrylic_thickness - led_height / 2
                + difference_fudge / 2
        ])
        cuboid([
            strip_length + led_wire_allotment * 2, 
            led_width + difference_fudge, 
            led_height + difference_fudge
        ]);

        color("magenta")
        translate([
            0, 
            card_y_offset, 
            -card_height / 2 - acrylic_thickness - led_height - strip_height / 2
                + difference_fudge / 2
        ])
        cuboid([
            strip_length + led_wire_allotment * 2, 
            strip_width, 
            strip_height + difference_fudge
        ]);
    }
}

module card()
{
    color("red", 0.25)
    translate([0, card_y_offset, 0])
    cuboid([card_width, card_thickness, card_height]);
}

module led_strip()
{
    translate([0, card_y_offset, -strip_box_height])
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