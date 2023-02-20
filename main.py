import streamlit as st
import asyncio
from asyncua import Server, ua, Client
import subprocess
import os
import signal

process = None


def start_server():
    process = subprocess.Popen(["python", "server-minimal.py"])
    st.session_state.process = process
    st.session_state.is_server_on = True
    st.session_state.server_status = "ON"


def stop_server():
    process = st.session_state.process
    os.kill(process.pid, signal.SIGTERM)
    st.session_state.is_server_on = False
    st.session_state.server_status = "OFF"


async def read_node(client, node_path):
    try:
        node = client.get_node(node_path)
        node_value = await node.read_value()
        return node_value
    except Exception as e:
        print(f"Error reading node value: {e}")
        return None

async def write_node(client, node_path, value):
    try:
        node = client.get_node(node_path)
        #var = ua.DataValue(ua.Variant(value, ua.VariantType.Int64))
        #st.write((var))
        await node.write_value(float(value))
        return True
    except Exception as e:
        print(f"Error writing node value: {e}")
        return False

async def main():

    if "is_server_on" not in st.session_state:
        st.session_state.is_server_on = False
        st.session_state.server_status = "OFF"

    if st.session_state.is_server_on:
        status_color = "green"
    else:
        status_color = "red"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("Start Server", on_click=start_server)

    with col2:
        st.button("Stop Server", on_click=stop_server)

    with col3:
        st.write("Server Status:")
        st.markdown(f"<h1 style='text-align: center; color: {status_color};'>{st.session_state.server_status}</h1>",
                    unsafe_allow_html=True)

    if st.session_state.is_server_on:
        st.write("Read/Write OPC UA Nodes")

        client = Client("opc.tcp://localhost:4841/freeopcua/server/")
        await client.connect()
        st.write(client)
        node = client.get_node("ns=2;i=2")
        name = (await node.read_browse_name()).Name
        st.write("The name is", name)
        root =  client.get_root_node()
        objects = await root.get_child("0:Objects")
        nodes = await objects.get_children()
        for node in nodes:
            st.write(node.nodeid, "\n")


        node_id = st.text_input("Node ID to read/write", value="ns=2;i=2")

        col11, col12 = st.columns(2)
        with col11:
            read_button = st.button("Read Node Value")
            #st.write(f"Node Value: 0.0")
            if read_button:
                value = await read_node(client, node_id)
                st.write(f"Node Value: {value}")

        with col12:
            write_button = st.button("Write Node Value")
            newvalue = st.text_input("New Value")
            if write_button:
                await write_node(client, node_id, newvalue)
                value = await read_node(client, node_id)
                #asyncio.sleep(1)
                if float(value) == float(newvalue):
                    st.write("Node Value Written Correctly")
                else:
                    st.write("except", float(value) - float(newvalue))

        #st.write(type(process))

if __name__ == "__main__":
    asyncio.run(main())