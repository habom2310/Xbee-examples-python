import time




class DHT11Result:
    'DHT11 sensor result returned by DHT11.read() method'

    ERR_NO_ERROR = 0
    ERR_MISSING_DATA = 1
    ERR_CRC = 2

    error_code = ERR_NO_ERROR
    temperature = -1
    humidity = -1

    def __init__(self, error_code, temperature, humidity):
        self.error_code = error_code
        self.temperature = temperature
        self.humidity = humidity

    def is_valid(self):
        return self.error_code == DHT11Result.ERR_NO_ERROR


class DHT11:
    'DHT11 sensor reader class for XBee'

    
    def __init__(self, device, pin):
        self.__device = device
        self.__pin = pin
        # Number of bits to extract with the mask (__MASK)
        self.__MASK_NUM_BITS = 8

        # Bit mask to extract the less important __MAS_NUM_BITS bits of a number.
        self.__MASK = 0xFF
        
        

    def read(self):
        #RPi.GPIO.setup(self.__pin, RPi.GPIO.OUT)
        #self.__device.set_parameter("P2",utils.hex_string_to_bytes("05"))

        # # send initial high
        # self.__send_and_sleep(1, 0.07)
        t0 = time.time()
        # pull down to low
        self.__send_and_sleep(0, 0.7)
        print(time.time()-t0)
        # change to input using pull up
        self.__device.set_parameter("D3",self.hex_string_to_bytes("03"))
        print(self.__device.get_dio_value(self.__pin))
        # collect data into an array
        data = self.__collect_input()

        # parse lengths of all data pull up periods
        pull_up_lengths = self.__parse_data_pull_up_lengths(data)

        # if bit count mismatch, return error (4 byte data + 1 byte checksum)
        if len(pull_up_lengths) != 40:
            return DHT11Result(DHT11Result.ERR_MISSING_DATA, 0, 0)

        # calculate bits from lengths of the pull up periods
        bits = self.__calculate_bits(pull_up_lengths)

        # we have the bits, calculate bytes
        the_bytes = self.__bits_to_bytes(bits)

        # calculate checksum and check
        checksum = self.__calculate_checksum(the_bytes)
        if the_bytes[4] != checksum:
            return DHT11Result(DHT11Result.ERR_CRC, 0, 0)
        
        
        #self.__device.set_parameter("D3",utils.hex_string_to_bytes("05"))
        # ok, we have valid data, return it
        return DHT11Result(DHT11Result.ERR_NO_ERROR, the_bytes[2], the_bytes[0])

    def __send_and_sleep(self, output, sleep):
        if(output==1):
            self.__device.set_parameter("D3",self.hex_string_to_bytes("05"))
            print("set High")
            print(self.__device.get_dio_value(self.__pin))
            time.sleep(sleep)
        elif(output==0):
            self.__device.set_parameter("D3",self.hex_string_to_bytes("04"))
            print("set Low")
            print(self.__device.get_dio_value(self.__pin))
            time.sleep(sleep)
            
    def __collect_input(self):
        # collect the data while unchanged found
        unchanged_count = 0

        # this is used to determine where is the end of the data
        max_unchanged_count = 100

        last = -1
        data = []
        while True:
            current = self.__device.get_dio_value(self.__pin)
            
            data.append(current)
            if last != current:
                unchanged_count = 0
                last = current
            else:
                unchanged_count += 1
                if unchanged_count > max_unchanged_count:
                    break
        print(len(data))
        print(data)
        return data

    def __parse_data_pull_up_lengths(self, data):
        STATE_INIT_PULL_DOWN = 1
        STATE_INIT_PULL_UP = 2
        STATE_DATA_FIRST_PULL_DOWN = 3
        STATE_DATA_PULL_UP = 4
        STATE_DATA_PULL_DOWN = 5

        state = STATE_INIT_PULL_DOWN

        lengths = [] # will contain the lengths of data pull up periods
        current_length = 0 # will contain the length of the previous period

        for i in range(len(data)):

            current = data[i]
            current_length += 1

            if state == STATE_INIT_PULL_DOWN:
                if current == 4:#IOValue.LOW:
                    # ok, we got the initial pull down
                    state = STATE_INIT_PULL_UP
                    continue
                else:
                    continue
            if state == STATE_INIT_PULL_UP:
                if current == 5:#IOValue.HIGH:
                    # ok, we got the initial pull up
                    state = STATE_DATA_FIRST_PULL_DOWN
                    continue
                else:
                    continue
            if state == STATE_DATA_FIRST_PULL_DOWN:
                if current == 4:#IOValue.LOW:
                    # we have the initial pull down, the next will be the data pull up
                    state = STATE_DATA_PULL_UP
                    continue
                else:
                    continue
            if state == STATE_DATA_PULL_UP:
                if current == 5:#IOValue.HIGH:
                    # data pulled up, the length of this pull up will determine whether it is 0 or 1
                    current_length = 0
                    state = STATE_DATA_PULL_DOWN
                    continue
                else:
                    continue
            if state == STATE_DATA_PULL_DOWN:
                if current == 4:#IOValue.LOW:
                    # pulled down, we store the length of the previous pull up period
                    lengths.append(current_length)
                    state = STATE_DATA_PULL_UP
                    continue
                else:
                    continue

        return lengths

    def __calculate_bits(self, pull_up_lengths):
        # find shortest and longest period
        shortest_pull_up = 1000
        longest_pull_up = 0

        for i in range(0, len(pull_up_lengths)):
            length = pull_up_lengths[i]
            if length < shortest_pull_up:
                shortest_pull_up = length
            if length > longest_pull_up:
                longest_pull_up = length

        # use the halfway to determine whether the period it is long or short
        halfway = shortest_pull_up + (longest_pull_up - shortest_pull_up) / 2
        bits = []

        for i in range(0, len(pull_up_lengths)):
            bit = False
            if pull_up_lengths[i] > halfway:
                bit = True
            bits.append(bit)

        return bits

    def __bits_to_bytes(self, bits):
        the_bytes = []
        byte = 0

        for i in range(0, len(bits)):
            byte = byte << 1
            if (bits[i]):
                byte = byte | 1
            else:
                byte = byte | 0
            if ((i + 1) % 8 == 0):
                the_bytes.append(byte)
                byte = 0

        return the_bytes

    def __calculate_checksum(self, the_bytes):
        return the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3] & 255
        
        
    def hex_string_to_bytes(self, hex_string):
        """
        Converts a String (composed by hex. digits) into a bytearray with same digits.
        
        Args:
            hex_string (String): String (made by hex. digits) with "0x" header or not.

        Returns:
            Bytearray: bytearray containing the numeric value of the hexadecimal digits.
            
        Raises:
            ValueError: if invalid literal for int() with base 16 is provided.
        
        Example:
            >>> a = "0xFFFE"
            >>> for i in hex_string_to_bytes(a): print(i)
            255
            254
            >>> print(type(hex_string_to_bytes(a)))
            <type 'bytearray'>
            
            >>> b = "FFFE"
            >>> for i in hex_string_to_bytes(b): print(i)
            255
            254
            >>> print(type(hex_string_to_bytes(b)))
            <type 'bytearray'>
            
        """
        aux = int(hex_string, 16)
        return self.int_to_bytes(aux)
    
    
    def int_to_bytes(self, number, num_bytes=None):
        """
        Converts the provided integer into a bytearray.
        
        If ``number`` has less bytes than ``num_bytes``, the resultant bytearray
        is filled with zeros (0x00) starting at the beginning.
        
        If ``number`` has more bytes than ``num_bytes``, the resultant bytearray
        is returned without changes.
        
        Args:
            number (Integer): the number to convert to a bytearray.
            num_bytes (Integer): the number of bytes that the resultant bytearray will have.

        Returns:
            Bytearray: the bytearray corresponding to the provided number.

        Example:
            >>> a=0xFFFE
            >>> print([i for i in int_to_bytes(a)])
            [255,254]
            >>> print(type(int_to_bytes(a)))
            <type 'bytearray'>
            
        """
        byte_array = bytearray()
        byte_array.insert(0, number & self.__MASK)
        number >>= self.__MASK_NUM_BITS
        while number != 0:
            byte_array.insert(0, number & self.__MASK)
            number >>= self.__MASK_NUM_BITS

        if num_bytes is not None:
            while len(byte_array) < num_bytes:
                byte_array.insert(0, 0x00)

        return byte_array   
        
        