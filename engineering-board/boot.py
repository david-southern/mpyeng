import usb_cdc

# USB_cdc enabled both the standard 'console' Serial that supports the REPL and the logging Serial connection, and also
# a 'data' Serial that can be used for protocol comms without disrupting the console logging.
usb_cdc.enable(console=True, data=True)
