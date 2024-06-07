import socket
import asyncio
import os

INTERFACE, SPORT = 'localhost', 8080
CHUNK = 100


intro_message = "Hello! Welcome to my (lyakhovs) server! I'm majoring in CS\n"

# TODO: Implement me for Part 1!
async def send_intro_message(writer, message):

    writer.write(intro_message.encode())
    await writer.drain()


# TODO: Implement me for Part 2!
async def receive_long_message(reader: asyncio.StreamReader):
    # First we receive the length of the message: this should be 8 total hexadecimal digits!
    # Note: `socket.MSG_WAITALL` is just to make sure the data is received in this case.
    data_length_hex = await reader.readexactly(8)

    # Then we convert it from hex to integer format that we can work with
    data_length = int(data_length_hex, 16)

    full_data = await reader.readexactly(data_length)
    return full_data.decode()


async def handle_client(reader, writer):
    """
    Part 1: Introduction
    """
    # TODO: send the introduction message by implementing `send_intro_message` above.
    await send_intro_message(writer, intro_message)

    """
    Part 2: Long Message Exchange Protocol
    """

    # Receive the filename from the client
    filename = await receive_long_message(reader)

    # Send an acknowledgement
    await send_intro_message(writer, "ACK")

    # TODO: Implement function above
    message = await receive_long_message(reader)

    # Write the contents of the long message into a file
    with open("./server_data/" + filename, 'w') as f:
        f.write(message)

    print("Wrote to file ./server_data/" + filename)

    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(
            handle_client,
            INTERFACE, SPORT
    )

    async with server:
        await server.serve_forever()

# Run the `main()` function
if __name__ == "__main__":
    asyncio.run(main())
