"""
Oregon State University, Computer Networks CS 372
Spring 2024
Will Richards, Chris Milford
"""

import socket
import asyncio
import os
from time import sleep

INTERFACE, SPORT = 'localhost', 8080
CHUNK = 100

PASSWORD = "HelloWorld"
intro_message = "Hello! Welcome to my (richawil & milfordc's) server! We are majoring in CS and ECE respectively\n"

async def sendMessage(writer, message):
    if message[len(message) - 1] != '\n':
        message += '\n'
    writer.write(message.encode())
    await writer.drain()


async def receive_long_message(reader: asyncio.StreamReader):
    # First we receive the length of the message: this should be 8 total hexadecimal digits!
    # Note: `socket.MSG_WAITALL` is just to make sure the data is received in this case.
    data_length_hex = await reader.readexactly(8)

    # Then we convert it from hex to integer format that we can work with
    data_length = int(data_length_hex, 16)

    full_data = await reader.readexactly(data_length)
    return full_data.decode()

async def passwordLogin(reader, writer):
    """
    The first thing we should do when we receive a new connection is wait for a password to be sent
    """
    loginSuccess = False
    for i in range(3):
        password = await receive_long_message(reader)
        print(password)
        if password == PASSWORD:
            await sendMessage(writer, intro_message)
            loginSuccess = True
            break
        else:
            print(f"Incorrect password {i+1}/3")
            await sendMessage(writer, "NAK Incorrect Password")
    
    return loginSuccess

async def handleCommands(reader, writer):
    while True:
        try:
            command = await receive_long_message(reader)
            # If the list command is used
            if command == "list":
                fileList = "\n".join(os.listdir("."))
                await sendMessage(writer, "ACK")
                await sendMessage(writer, fileList)
            
            # If we are downloading a file from the server
            elif command.startswith("put"):
                splitCommand = command.split(" ")
                await sendMessage(writer, "ACK")
                with open(splitCommand[1], 'w') as file:
                        length = file.write(await receive_long_message(reader))
                        if length > 0:
                            await sendMessage(writer, "ACK")
                        else:
                            await sendMessage(writer, "Failed to write files")
                        
            # If we are downloading a file from the server
            elif command.startswith("get"):
                splitCommand = command.split(" ")
                if os.path.exists(splitCommand[1]):
                    await sendMessage(writer, "ACK")
                    with open(splitCommand[1], 'r') as file:
                        await sendMessage(writer, file.read())
                else:
                    await sendMessage(writer, "NAK File does not exist")
            
            # If we are removing a file on the server
            elif command.startswith("remove"):
                splitCommand = command.split(" ")
                if os.path.exists(splitCommand[1]):
                    await sendMessage(writer, "ACK")
                    os.remove(splitCommand[1])
                else:
                    await sendMessage(writer, "NAK File does not exist")

            # If we are attempting to close the connection
            elif command == "close":
                await sendMessage(writer, "ACK")
                writer.close()
                await writer.wait_closed()
                break
            else:
                await sendMessage(writer, "NAK Invalid Command")

        except KeyboardInterrupt:
            break

async def handle_client(reader, writer):
    
    # Kill the connection if the password was entered incorrectly too many times
    if not await passwordLogin(reader, writer):
        writer.close()
        await writer.wait_closed()
        return

    # Process the commands used by this server
    await handleCommands(reader, writer)

    writer.close()
    await writer.wait_closed()
    print("Remote connection closed.")


async def main():
    server = await asyncio.start_server(
            handle_client,
            INTERFACE, SPORT
    )

    async with server:
        print(f"Server started on {INTERFACE} on port {SPORT}")
        await server.serve_forever()

# Run the `main()` function
if __name__ == "__main__":
    os.chdir("myfiles")
    asyncio.run(main())
