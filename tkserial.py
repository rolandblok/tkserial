# simple tkinter program to send and receive serial data

# open a tkinter window with big uneditable text box
# and a small text box for entering data to send
# and a button to send the data
# drop down menu to select the serial port



import threading
import tkinter as tk
import serial
import time

gbl_ser_con = None
glb_speed = 115200
glb_read_thread = None
glb_command_history = []
glb_current_command_index = -1

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

def read_data():
    global gbl_ser_con
    while True:
        if gbl_ser_con:
            try:
                # read data from the serial port
                data = gbl_ser_con.readline()
                if data:
                    # make the text box editable
                    text.config(state=tk.NORMAL)
                    text.insert(tk.END, data.decode())
                    # make the text box not editable
                    text.see(tk.END)
                    text.config(state=tk.DISABLED)
                time.sleep(0.01)
            except serial.SerialException:
                print("Serial Exception")
                gbl_ser_con = None
                break
        else :
            break
    
# connect to a serial port
def connect(port):
    global gbl_ser_con
    gbl_ser_con = serial.Serial(port, glb_speed, timeout=1)
    # add connected to textboard
    text.config(state=tk.NORMAL)
    text.insert(tk.END, "Connected to " + port + "\n")
    text.config(state=tk.DISABLED)

    # start a thread to read data from the serial port
    glb_read_thread = threading.Thread(target=read_data)
    glb_read_thread.start()
    # set the title of the window to the port name
    root.title("Serial Terminal connected to " + port)

def stop_thread():
    global gbl_ser_con
    if gbl_ser_con:
        gbl_ser_con.close()
        gbl_ser_con = None
        print("Disconnected")
    # stop the thread
    if glb_read_thread:
        glb_read_thread.join()

def quit():
    stop_thread()
    root.quit()

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
menubar.add_cascade(
    label="File",
    menu=file_menu
)

# list all serial ports
ports = list_ports()
serial_menu = tk.Menu(menubar)
for port, desc, hwid in sorted(ports):
    serial_menu.add_command(label=port, command=lambda port=port: connect(port))
serial_menu.add_separator()
serial_menu.add_command(label="Disconnect", command=stop_thread)
menubar.add_cascade(label="Serial Ports", menu=serial_menu)

# create the text box, that scales with the window, not editable
text = tk.Text(root)
text.pack(fill=tk.BOTH, expand=True)
# make text not editable
text.config(state=tk.DISABLED)

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



