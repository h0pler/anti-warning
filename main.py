import asyncio
import ssl
import asyncio

import proxymaster


def modify_request(request_data):
    modified_request = request_data.decode("utf-8")
    modified_request = modified_request.replace("Proxy-Connection: keep-alive\r\n", "")
    modified_request = modified_request.replace(
        "\r\n\r\n", f"\r\nX-Forwarded-For: 1.1.1.1\r\n\r\n", 1
    )
    return modified_request.encode("utf-8")

async def relay_data(reader, writer, data_size=float("inf"), response=False):
    try:
        total_data = b""
        while data_size > 0:
            data = await asyncio.wait_for(
                reader.read(min(4096, data_size)), timeout=10
            )
            if not data:
                break
            total_data += data
            data_size -= len(data)

        if response:
            writer.write(total_data)
            await writer.drain()

    except asyncio.CancelledError:
        pass
    except ConnectionResetError as e:
        print(f"Connection reset by peer: {e}")
    except asyncio.TimeoutError as e:
        print(f"Timeout in relay_data: {e}")
    except Exception as e:
        print(f"Error in relay_data: {e}")
    finally:
        writer.close()

async def handle_connect_method(reader, writer, proxy_host, proxy_port):
    try:
        data = await reader.readuntil(b"\r\n\r\n")
        first_line = data.decode().split("\r\n")[0]
        _, _, address = first_line.partition(" ")
        _, _, host_port = address.partition(":")
        host, _, port = host_port.rpartition(":")

        writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
        await writer.drain()

        print(host, port)
        if port == "443":
            ssl_context = ssl.create_default_context()
            remote_reader, remote_writer = await asyncio.open_connection(
                host, port, ssl=ssl_context
            )

            ssl_remote_reader = ssl_context.wrap_socket(
                remote_reader, server_hostname=host
            )
            ssl_remote_writer = ssl_context.wrap_socket(
                remote_writer, server_hostname=host
            )

            await asyncio.gather(
                relay_data(reader, ssl_remote_writer),
                relay_data(ssl_remote_reader, writer),
            )

            server_cert = ssl_remote_reader.getpeercert(binary_form=True)
            writer.write(server_cert)
            await writer.drain()
        else:
            remote_reader, remote_writer = await asyncio.open_connection(host, port)

            await asyncio.gather(
                relay_data(reader, remote_writer), relay_data(remote_reader, writer)
            )

    except Exception as e:
        print(f"Error in handle_connect_method: {e}")

async def handle_client(reader, writer, proxy_host, proxy_port):
    try:
        client_request = b""
        while True:
            chunk = await reader.read(4096)
            if not chunk:
                break
            client_request += chunk

            if b"\r\n\r\n" in client_request:
                break

        print("Received client request: ", client_request.decode("utf-8"))

        first_line = client_request.decode().split("\r\n")[0]
        method, _, _ = first_line.partition(" ")

        if method.upper() == "CONNECT":
            await handle_connect_method(reader, writer, proxy_host, proxy_port)
            return

        if method.upper() in (
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "HEAD",
            "OPTIONS",
            "PATCH",
        ):
            modified_request = modify_request(client_request)
        else:
            modified_request = client_request

        try:
            destination_reader, destination_writer = await asyncio.open_connection(
                proxy_host, proxy_port
            )
            print("Connected")
        except Exception as e:
            print(f"Failed to connect to proxy: {e}")
            writer.close()
            return

        print(f"Modified: {modified_request}")
        destination_writer.write(modified_request)
        await destination_writer.drain()
        await relay_data(destination_reader, writer, response=True)

    except asyncio.CancelledError:
        print("cancelled")
        pass
    except ConnectionResetError as e:
        print(f"Connection reset by peer: {e}")
        writer.close()
    except Exception as e:
        print(f"Error in handle_client: {e}")
    finally:
        writer.close()

async def proxy_server():
    proxy = await proxymaster.get()
    proxy_host = proxy[0]
    proxy_port = proxy[1]

    server_host = "0.0.0.0"
    server_port = 10000
    print(f"{proxy_host}:{proxy_port}")
    server = await asyncio.start_server(
        lambda reader, writer: asyncio.ensure_future(
            handle_client(reader, writer, proxy_host, proxy_port)
        ),
        server_host,
        server_port,
    )

    print(
        f"Proxy server is ready to receive connections on {server_host}:{server_port}"
    )

    async def serve():
        try:
            async with server:
                await server.serve_forever()
        except Exception as e:
            print(f"Error in proxy_server: {e}")

    await asyncio.create_task(serve())

async def main():
    proxy_task = asyncio.create_task(proxy_server())
    await proxy_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
