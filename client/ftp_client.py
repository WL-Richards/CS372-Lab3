"""
Oregon State University, Computer Networks CS 372
Spring 2024
Will Richards, Chris Milford
"""

import os
import socket
from time import sleep
from threading import Thread
import asyncio

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


async def sendPassword(reader, writer):
    # Prompt the user 3 times for the password exiting early if it is the correct password
    for i in range(3):
        password = input("Enter password: ")
        await send_long_message(writer, password)
        recvMessage = await recv_message(reader)
        if not recvMessage.startswith("NAK"):
            print(recvMessage)
            return True
        else:
            print("Incorrect password")

    return False
    

async def ftpOptions(reader, writer):
    # Prompt the user for a command over an over
    while True:
        try:
            option = input("> ")
            option = option.strip()

            # Check if file exists
            if option.startswith("put") and not os.path.exists(option.split(" ")[1]):
                print("No file exists")
                continue

            await send_long_message(writer, option)
            response = (await recv_message(reader)).strip()
            # If we wanted to close and the server responded with an ack we should exit our loop
            if option == "close" and response.startswith("ACK"):
                break

            # If we were trying to list the files we should check if our initial response was an ack and then we should receive the list of files
            if option == "list":
                if response == "ACK":
                    print("\n".join((await recv_message(reader)).split(":")))     
                
            # Download files from the server
            elif option.startswith("get"):
                if response == "ACK":
                    fileContents = await recv_message(reader)
                    with open(option.split(" ")[1], 'w') as file:
                        file.write(fileContents)
                else:
                    print(response)

            # Upload files to the server
            elif option.startswith("put"):
                if response == "ACK":
                    with open(option.split(" ")[1], 'r') as file:
                        await send_long_message(writer, file.read())
                    response = (await recv_message(reader)).strip()
                    if response != "ACK":
                        print(response)
                else:
                    print(response)


            # If anything else just print the response
            else:
                print(response)
        except KeyboardInterrupt:
            break


async def connect():
    # Configure a socket object to use IPv4 and TCP
    reader, writer = await asyncio.open_connection(IP, DPORT)

    try:

        # If we failed to send the correct password we should exit
        if not await sendPassword(reader, writer):
            print("Password retries exceeded.")
            return
        
        await ftpOptions(reader, writer)

    finally:
        writer.close()
        await writer.wait_closed()

    return 0

async def main():
    await connect()

# Run the `main()` function
if __name__ == "__main__":
    os.chdir("myfiles")
    asyncio.run(main())


