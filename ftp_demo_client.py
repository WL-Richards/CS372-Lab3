import socket
from time import sleep
from threading import Thread
import asyncio
import os

IP, DPORT = 'localhost', 8080

# Helper function that converts integer into 8 hexadecimal digits
# Assumption: integer fits in 8 hexadecimal digits
def to_hex(number):
    # Verify our assumption: error is printed and program exists if assumption is violated
    assert number <= 0xffffffff, "Number too large"
    return "{:08x}".format(number)

# TODO: Implement me for Part 1!
async def recv_message(reader: asyncio.StreamReader):
    full_data = await reader.readline()
    return full_data.decode()
    

# TODO: Implement me for Part 2!
async def send_long_message(writer: asyncio.StreamWriter, data):
    # TODO: Send the length of the message: this should be 8 total hexadecimal digits
    #       This means that ffffffff hex -> 4294967295 dec
    #       is the maximum message length that we can send with this method!
    #       hint: you may use the helper function `to_hex`. Don't forget to encode before sending!

    writer.write(to_hex(len(data)).encode())
    writer.write(data.encode())

    await writer.drain()


async def connect(i):
    # Configure a socket object to use IPv4 and TCP
    reader, writer = await asyncio.open_connection(IP, DPORT)

    """
    Part 1: Introduction
    """

    try:
        # TODO: receive the introduction message by implementing `recv_intro_message` above.
        intro = await recv_message(reader)
        print(intro)

        # Get the filename to send from the user
        filename = ""
        while True:
            filename = input("Enter filename to send: ")
            if os.path.isfile("./client_data/" + filename):
                break
            print("Invalid filename.")

        # Send the filename to the server
        await send_long_message(writer, filename)

        # Receive a response from the server
        await recv_message(reader)


        # Read in the contents of the file
        with open("./client_data/" + filename, 'r') as f:
            tosend = f.read()

        # Send the file contents to the server
        long_msg = f"{tosend}"

        """
        Part 2: Long Message Exchange Protocol
        """
        # TODO: Send message to the server by implementing `send_long_message` above.
        await send_long_message(writer, long_msg)

    finally:
        writer.close()
        await writer.wait_closed()



    return 0

async def main(tosend):
    tasks = []
    for i in range(1):
        tasks.append(connect(tosend  + str(i).rjust(8, '0')))
    #await connect(str(0).rjust(8, '0'))

    await asyncio.gather(*tasks)
    print("done")

# Run the `main()` function
if __name__ == "__main__":
    with open("./client_data/script.txt", 'r') as f:
        tosend = f.read()
    
    asyncio.run(main(tosend))
