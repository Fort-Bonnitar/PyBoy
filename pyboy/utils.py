#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

STATE_VERSION = 9

##############################################################
# Buffer classes


class IntIOInterface:
    def __init__(self, buf):
        pass

    def write(self, byte):
        raise Exception("Not implemented!")

    def write_64bit(self, value):
        self.write(value & 0xFF)
        self.write((value >> 8) & 0xFF)
        self.write((value >> 16) & 0xFF)
        self.write((value >> 24) & 0xFF)
        self.write((value >> 32) & 0xFF)
        self.write((value >> 40) & 0xFF)
        self.write((value >> 48) & 0xFF)
        self.write((value >> 56) & 0xFF)

    def read_64bit(self):
        a = self.read()
        b = self.read()
        c = self.read()
        d = self.read()
        e = self.read()
        f = self.read()
        g = self.read()
        h = self.read()
        return a | (b << 8) | (c << 16) | (d << 24) | (e << 32) | (f << 40) | (g << 48) | (h << 56)

    def write_32bit(self, value):
        self.write(value & 0xFF)
        self.write((value >> 8) & 0xFF)
        self.write((value >> 16) & 0xFF)
        self.write((value >> 24) & 0xFF)

    def read_32bit(self):
        a = self.read()
        b = self.read()
        c = self.read()
        d = self.read()
        return int(a | (b << 8) | (c << 16) | (d << 24))

    def write_16bit(self, value):
        self.write(value & 0xFF)
        self.write((value >> 8) & 0xFF)

    def read_16bit(self):
        a = self.read()
        b = self.read()
        return int(a | (b << 8))

    def read(self):
        raise Exception("Not implemented!")

    def seek(self, pos):
        raise Exception("Not implemented!")

    def flush(self):
        raise Exception("Not implemented!")

    def new(self):
        raise Exception("Not implemented!")

    def commit(self):
        raise Exception("Not implemented!")

    def seek_frame(self, _):
        raise Exception("Not implemented!")

    def tell(self):
        raise Exception("Not implemented!")


class IntIOWrapper(IntIOInterface):
    """
    Wraps a file-like object to allow writing integers to it.
    This allows for higher performance, when writing to a memory map in rewind.
    """
    def __init__(self, buf):
        self.buffer = buf

    def write(self, byte):
        assert isinstance(byte, int)
        assert 0 <= byte <= 0xFF
        return self.buffer.write(byte.to_bytes(1, "little"))

    def read(self):
        # assert count == 1, "Only a count of 1 is supported"
        data = self.buffer.read(1)
        assert len(data) == 1, "No data"
        return ord(data)

    def seek(self, pos):
        self.buffer.seek(pos)

    def flush(self):
        self.buffer.flush()

    def tell(self):
        return self.buffer.tell()


##############################################################
# Misc


# TODO: Would a lookup-table increase performance? For example a lookup table of each 4-bit nibble?
# That's 16**2 = 256 values. Index calculated as: (byte1 & 0xF0) | ((byte2 & 0xF0) >> 4)
# and then: (byte1 & 0x0F) | ((byte2 & 0x0F) >> 4)
# Then could even be preloaded for each color palette
def color_code(byte1, byte2, offset):
    """Convert 2 bytes into color code at a given offset.

    The colors are 2 bit and are found like this:

    Color of the first pixel is 0b10
    | Color of the second pixel is 0b01
    v v
    1 0 0 1 0 0 0 1 <- byte1
    0 1 1 1 1 1 0 0 <- byte2
    """
    return (((byte2 >> (offset)) & 0b1) << 1) + ((byte1 >> (offset)) & 0b1)


def flatten_list(l):
    flat_list = []
    for sublist in l:
        for item in sublist:
            flat_list.append(item)
    return flat_list


##############################################################
# Window Events
# Temporarily placed here to not be exposed on public API


class WindowEvent:
    """
    All supported events can be found in the class description below.

    It can be used as follows:

    >>> from pyboy import PyBoy, WindowEvent
    >>> pyboy = PyBoy('file.rom')
    >>> pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
    """

    # ONLY ADD NEW EVENTS AT THE END OF THE LIST!
    # Otherwise, it will break replays, which depend on the id of the event
    (
        QUIT,
        PRESS_ARROW_UP,
        PRESS_ARROW_DOWN,
        PRESS_ARROW_RIGHT,
        PRESS_ARROW_LEFT,
        PRESS_BUTTON_A,
        PRESS_BUTTON_B,
        PRESS_BUTTON_SELECT,
        PRESS_BUTTON_START,
        RELEASE_ARROW_UP,
        RELEASE_ARROW_DOWN,
        RELEASE_ARROW_RIGHT,
        RELEASE_ARROW_LEFT,
        RELEASE_BUTTON_A,
        RELEASE_BUTTON_B,
        RELEASE_BUTTON_SELECT,
        RELEASE_BUTTON_START,
        _INTERNAL_TOGGLE_DEBUG,
        PRESS_SPEED_UP,
        RELEASE_SPEED_UP,
        STATE_SAVE,
        STATE_LOAD,
        PASS,
        SCREEN_RECORDING_TOGGLE,
        PAUSE,
        UNPAUSE,
        PAUSE_TOGGLE,
        PRESS_REWIND_BACK,
        PRESS_REWIND_FORWARD,
        RELEASE_REWIND_BACK,
        RELEASE_REWIND_FORWARD,
        WINDOW_FOCUS,
        WINDOW_UNFOCUS,
        _INTERNAL_RENDERER_FLUSH,
        _INTERNAL_MOUSE,
        _INTERNAL_MARK_TILE,
        SCREENSHOT_RECORD,
        DEBUG_MEMORY_SCROLL_DOWN,
        DEBUG_MEMORY_SCROLL_UP,
        MOD_SHIFT_ON,
        MOD_SHIFT_OFF,
        FULL_SCREEN_TOGGLE,
    ) = range(42)

    def __init__(self, event):
        self.event = event

    def __eq__(self, x):
        if isinstance(x, int):
            return self.event == x
        else:
            return self.event == x.event

    def __int__(self):
        return self.event

    def __str__(self):
        return (
            "QUIT",
            "PRESS_ARROW_UP",
            "PRESS_ARROW_DOWN",
            "PRESS_ARROW_RIGHT",
            "PRESS_ARROW_LEFT",
            "PRESS_BUTTON_A",
            "PRESS_BUTTON_B",
            "PRESS_BUTTON_SELECT",
            "PRESS_BUTTON_START",
            "RELEASE_ARROW_UP",
            "RELEASE_ARROW_DOWN",
            "RELEASE_ARROW_RIGHT",
            "RELEASE_ARROW_LEFT",
            "RELEASE_BUTTON_A",
            "RELEASE_BUTTON_B",
            "RELEASE_BUTTON_SELECT",
            "RELEASE_BUTTON_START",
            "_INTERNAL_TOGGLE_DEBUG",
            "PRESS_SPEED_UP",
            "RELEASE_SPEED_UP",
            "STATE_SAVE",
            "STATE_LOAD",
            "PASS",
            "SCREEN_RECORDING_TOGGLE",
            "PAUSE",
            "UNPAUSE",
            "PAUSE_TOGGLE",
            "PRESS_REWIND_BACK",
            "PRESS_REWIND_FORWARD",
            "RELEASE_REWIND_BACK",
            "RELEASE_REWIND_FORWARD",
            "WINDOW_FOCUS",
            "WINDOW_UNFOCUS",
            "_INTERNAL_RENDERER_FLUSH",
            "_INTERNAL_MOUSE",
            "_INTERNAL_MARK_TILE",
            "SCREENSHOT_RECORD",
            "DEBUG_MEMORY_SCROLL_DOWN",
            "DEBUG_MEMORY_SCROLL_UP",
            "MOD_SHIFT_ON",
            "MOD_SHIFT_OFF",
            "FULL_SCREEN_TOGGLE",
        )[self.event]


class WindowEventMouse(WindowEvent):
    def __init__(
        self, *args, window_id=-1, mouse_x=-1, mouse_y=-1, mouse_scroll_x=-1, mouse_scroll_y=-1, mouse_button=-1
    ):
        super().__init__(*args)
        self.window_id = window_id
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.mouse_scroll_x = mouse_scroll_x
        self.mouse_scroll_y = mouse_scroll_y
        self.mouse_button = mouse_button



# Gameshark Cheat Codes
class GameShark:
    def __init__(self):
        '''
        This class allows for the conversion and usage of Gameshark codes. The cheats_path should
        point to a saved .txt file containing the codes with the following format a name for the code and the code itself seperated by a space:
        {code_name} {code}

        Ex. 
        NoWildEncounters 01033CD1
        '''

        self.cheats_path = None
        self.cheats = {}
        self._update_codes()

    def set_path(self, path):
        self.cheats_path = path
        self._update_codes()


    def _get_cheats(self):
        with open(self.cheats_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split()
                if len(parts) == 2:
                    cheat_name, gameshark_code = parts[0], parts[1]
                    self._convert_cheat(cheat_name, gameshark_code)
                else:
                    print(f"Invalid line in cheats file: {line}")



    def _convert_cheat(self, cheat_name: str, gameshark_code: str):
        '''
        A GameShark code for these consoles is written in the format ttvvaaaa. tt specifies the code type and VRAM bank, which is usually 01. vv specifies the hexadecimal value the code will write into the game's memory. aaaa specifies the memory address that will be modified, with the low byte first (e.g. address C056 is written as 56C0).
        Example 011556C0 would output:
        location = 01
        value = 0x15
        address = 0x56C0
        '''
        # Check if the input cheat code has the correct length (8 characters)
        if len(gameshark_code) != 8:
            raise ValueError("Invalid cheat code length. Cheat code must be 8 characters long.")

        # Extract components from the cheat code
        code_type = gameshark_code[:2]
        value = int((f'0x{gameshark_code[2:4]}'), 16)  # Convert hexadecimal value to an integer
        print(f'converted value = 0x{gameshark_code[2:4]}')
        unconverted_address = gameshark_code[4:]  # Ex:   1ED1
        lower = unconverted_address[:2]  # Ex:  1E
        upper = unconverted_address[2:]  # Ex:  D1
        address_converted = '0x' + upper + lower   # Ex: 0xD11E   # Converting to Ram Readable address 
        print(f'converted address = {address_converted}')
        address = int(address_converted, 16)

        # Format the output
        formatted_output = {
            'location': code_type,
            'value': value,
            'address': address
        }
        self.cheats[cheat_name] = formatted_output



    def _update_codes(self):
        self.cheats = {}
        self._get_cheats()



