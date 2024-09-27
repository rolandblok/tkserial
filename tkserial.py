# simple tkinter program to send and receive serial data

# open a tkinter window with big uneditable text box
# and a small text box for entering data to send
# and a button to send the data
# drop down menu to select the serial port



import threading
import tkinter as tk
import serial
import time

baud_rates = [9600, 19200, 38400, 57600, 115200]

gbl_ser_con = None
glb_baud_rate = 115200
glb_read_thread = None
glb_command_history = []
glb_current_command_index = -1

# print version ktinter
print(tk.TkVersion)

def execute_command(event):
    global current_command_index, glb_current_command_index
    command = entry_widget.get()
    send_data(command)
    if command:  # Check if the command is not empty
        glb_command_history.append(command)  # Add command to history
        glb_current_command_index = len(glb_command_history)  # Reset the index
        entry_widget.delete(0, 'end')  # Clear the entry widget

def retrieve_next_command(event):
    retrieve_command(event, 1)

def retrieve_previous_command(event):
    retrieve_command(event, -1)

def retrieve_command(event, direction):
    global current_command_index, glb_current_command_index
    print(glb_current_command_index, glb_command_history)
    if glb_command_history:  # Check if there is any command in the history
        # Calculate new index position
        new_index = glb_current_command_index + direction
        
        # Clamp the new index to be within the valid range
        new_index = max(0, min(new_index, len(glb_command_history) - 1))
        
        # Update the global index
        glb_current_command_index = new_index

        # Retrieve and display the command at the new index
        previous_command = glb_command_history[glb_current_command_index]
        entry_widget.delete(0, 'end')  # Clear the current entry
        entry_widget.insert(0, previous_command)  # Insert the previous command

# List all serial ports
def list_ports():
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
    return ports

# Send data to the serial port
def send_data(command):
    global gbl_ser_con
    if gbl_ser_con:
        # get the text from the entry box
        gbl_ser_con.write(command.encode())

# add text to the text box
def add_line(line):
    # if line has no end of line, add it
    if not line.endswith('\n'):
        line += '\n'
    tk_text.config(state=tk.NORMAL)
    tk_text.insert(tk.END, line)
    tk_text.see(tk.END)
    tk_text.config(state=tk.DISABLED)

def read_data():
    global gbl_ser_con
    while True:
        if gbl_ser_con:
            try:
                # read data from the serial port
                data = gbl_ser_con.readline()
                if data:
                    # make the text box editable
                    add_line(data.decode())
                time.sleep(0.01)
            except serial.SerialException:
                print("Serial Exception")
                add_line("Serial Exception")
                gbl_ser_con = None
                break
        else :
            break
    
# connect to a serial port
def connect(port):
    global gbl_ser_con
    gbl_ser_con = serial.Serial(port, glb_baud_rate, timeout=1)
    # add connected to textboard
    add_line("Connected to " + port)

    # start a thread to read data from the serial port
    glb_read_thread = threading.Thread(target=read_data)
    glb_read_thread.start()
    # set the title of the window to the port name
    root.title("Serial Terminal connected to " + port + " at " + str(glb_baud_rate) + " baud")

# set the baud rate
def set_baud_rate(rate):
    global glb_baud_rate
    glb_baud_rate = rate
    print("Baud rate set to " + str(rate))
    # set the title of the window to the port name
    root.title("Serial Terminal " + str(rate))
    # Reset all menu items to default background color
    for index, r in enumerate(baud_rates):
        if r == glb_baud_rate:
            baud_menu.entryconfig(index+1, background='lightblue')
        else:
            baud_menu.entryconfig(index+1, background='gray')

# stop the thread and close the serial port            
def stop_thread():
    global gbl_ser_con
    if gbl_ser_con:
        gbl_ser_con.close()
        gbl_ser_con = None
        root.title("Serial Terminal disconnected, " + str(glb_baud_rate) + " baud")
        add_line("Disconnected")
        print("Disconnected")
    # stop the thread
    if glb_read_thread:
        glb_read_thread.join()

# close the window
def quit():
    stop_thread()
    root.quit()

def menu_ports():
    # list all serial ports and create serial selection menu
    ports = list_ports()

    # Check if the serial_menu already exists, if not, create it
    if 'serial_menu' not in globals():
        global serial_menu
        serial_menu = tk.Menu(menubar)
        menubar.add_cascade(label="Connect Serial", menu=serial_menu)

    # Clear the existing menu items
    serial_menu.delete(0, tk.END)

    # Add new items to the menu
    for port, desc, hwid in sorted(ports):
        serial_menu.add_command(label=port, command=lambda port=port: connect(port))
    
    # Add a separator and a disconnect option
    serial_menu.add_separator()
    serial_menu.add_command(label="Disconnect", command=stop_thread)

    

# create the main window, 
root = tk.Tk()
root.title("Serial Terminal - no connection")

# create a menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)

# create a file menu
file_menu = tk.Menu(menubar)
# add a quit command which will stop the thread and close the window
file_menu.add_command(label="Quit", command=quit)
menubar.add_cascade(label="File", menu=file_menu)

# Create a baud rate menu
baud_menu = tk.Menu(menubar)
for r in baud_rates:
    baud_menu.add_command(label=str(r), command=lambda rate=r: set_baud_rate(rate))
set_baud_rate(glb_baud_rate)
menubar.add_cascade(label="Baud Rate", menu=baud_menu)

# Create a serial menu
serial_menu = tk.Menu(menubar, postcommand=menu_ports)
# Add a list of serial ports    
menu_ports()
menubar.add_cascade(label="Connect Serial", menu=serial_menu)

# create the text box, that scales with the window, not editable
tk_text = tk.Text(root)
tk_text.pack(fill=tk.BOTH, expand=True)
# make text not editable
tk_text.config(state=tk.DISABLED)

# create the entry box, that scales with the width of the window
entry_widget = tk.Entry(root)
entry_widget.pack(fill=tk.X)
# Entry should always have the focus
entry_widget.focus_set()
# when somewhere is clicked the focus should go to the entry
root.bind('<Button-1>', lambda event: entry_widget.focus_set())


# when enter is pressed the message is sent
root.bind('<Return>', execute_command)

# if up is pressed the last command is entered
entry_widget.bind('<Up>', retrieve_previous_command)
# if up is pressed the last command is entered
entry_widget.bind('<Down>', retrieve_next_command)

# bind the close window
root.protocol("WM_DELETE_WINDOW", quit)

# show the window
root.mainloop()



