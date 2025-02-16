import streamlit as st
import streamlit.components.v1 as components
import asyncio
import pyaudio
import queue
import asyncio
import base64
import json
import websockets
from concurrent.futures import ThreadPoolExecutor

import base64

from loguru import logger
from settings import settings

from utils.hume_utils.authenticator import Authenticator
from utils.hume_utils.connection import Connection
from utils.hume_utils.devices import AudioDevices
from utils.audio_visualizer import lottie_audio_visualizer

# Audio format and parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_WIDTH = 2
CHUNK_SIZE = 1024

st.logo(
    image="media/mainlogo.png",
    size="large"
)

# Set up a thread pool executor for non-blocking audio stream reading
executor = ThreadPoolExecutor(max_workers=1)
    
class StreamlitAudioChat:
    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
        self.audio_stream = None
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.task = None
        
    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'access_token' not in st.session_state:
            st.session_state.access_token = None
        if 'selected_input_device' not in st.session_state:
            st.session_state.selected_input_device = None
        if 'selected_output_device' not in st.session_state:
            st.session_state.selected_output_device = None
        if 'is_input_device_selected' not in st.session_state:
            st.session_state.is_input_device_selected = False
        if 'is_output_device_selected' not in st.session_state:
            st.session_state.is_output_device_selected = False
        if 'selected_input_device_name' not in st.session_state:
            st.session_state.selected_input_device_name = None
        if 'selected_output_device_name' not in st.session_state:
            st.session_state.selected_output_device_name = None

    def get_audio_devices(self):
        """
        Get available audio input and output devices
        """
        return AudioDevices.list_audio_devices(self.pyaudio)

    def authenticate(self):
        """
        Handle authentication with Hume AI
        """

        st.sidebar.header("Authentication")
        
        # Load environment variables
        api_key = settings.HUME_API_KEY or st.sidebar.text_input("Hume API Key", type="password")
        secret_key = settings.HUME_SECRET_KEY or st.sidebar.text_input("Hume Secret Key", type="password")
        
        if st.sidebar.button("Authenticate", use_container_width=True, type="primary"):
            if api_key and secret_key:
                try:
                    authenticator = Authenticator(api_key, secret_key)
                    access_token = authenticator.fetch_access_token()
                    st.session_state.access_token = access_token
                    st.session_state.authenticated = True
                    st.sidebar.success("Authentication successful!")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Authentication failed: {str(e)}")
            else:
                st.sidebar.error("Please provide both API Key and Secret Key")

    def setup_audio_devices(self):
        """
        Setup audio input and output devices
        """

        st.sidebar.header("Audio Device Setup")
        
        input_devices, output_devices = self.get_audio_devices()
        
        # Input device selection
        input_device_names = [f"{name} ({idx})" for idx, name, _ in input_devices]
        selected_input = st.sidebar.selectbox(
            "Select Input Device",
            input_device_names,
            index=0 if input_device_names else None
        )
        st.session_state.selected_input_device_name = selected_input
        
        # Output device selection
        output_device_names = [f"{name} ({idx})" for idx, name, _ in output_devices]
        selected_output = st.sidebar.selectbox(
            "Select Output Device",
            output_device_names,
            index=0 if output_device_names else None
        )
        st.session_state.selected_output_device_name = selected_output
        
        if st.sidebar.button("Configure Devices", use_container_width=True, type="primary") and selected_input and selected_output:
            try:
                input_idx = int(selected_input.split("(")[-1].strip(")"))
                output_idx = int(selected_output.split("(")[-1].strip(")"))
                
                # Find the selected input device's sample rate
                input_device = next((device for device in input_devices if device[0] == input_idx), None)
                # if input_device:
                sample_rate = input_device[2]
                
                # Store selected devices in session state
                st.session_state.selected_input_device = (input_idx, sample_rate)
                st.session_state.selected_output_device = output_idx
                st.session_state.is_input_device_selected = True
                st.session_state.is_output_device_selected = True
                st.sidebar.success("Audio devices configured successfully!")
                # else:
                #     st.sidebar.error("Failed to get input device information")
            except:
                st.sidebar.error("Please select both input and output devices")

            st.rerun()

    def stop_chat(self):
        """
        Set chat as inactive and trigger rerun
        """
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None

    async def start_audio_stream(self, lottie_json_str):
        """
        Start the audio stream with WebSocket connection
        """
        if not all([
            st.session_state.authenticated,
            st.session_state.is_input_device_selected,
            st.session_state.is_output_device_selected,
        ]):
            st.error("Please complete authentication and device setup first")
            return

        input_idx, sample_rate = st.session_state.selected_input_device
        output_idx = st.session_state.selected_output_device

        # Initialize audio stream
        self.audio_stream = self.pyaudio.open(
            format=FORMAT,
            channels=CHANNELS,
            frames_per_buffer=CHUNK_SIZE,
            rate=sample_rate,
            input=True,
            output=True,
            input_device_index=input_idx,
            output_device_index=output_idx,
        )

        # Construct WebSocket URL
        socket_url = (
            "wss://api.hume.ai/v0/assistant/chat?"
            f"access_token={st.session_state.access_token}"
        )

        websocket_connection = Connection()

        while True:
            try:
                async with websockets.connect(socket_url) as socket:
                    logger.info("Connected to WebSocket")
                    send_task = asyncio.create_task(
                        websocket_connection._send_audio_data(
                            socket,
                            self.audio_stream,
                            sample_rate,
                            SAMPLE_WIDTH,
                            CHANNELS,
                            CHUNK_SIZE,
                        )
                    )

                    #---------- FIXES ----------
                    receive_task = asyncio.create_task(websocket_connection._receive_audio_data(socket, lottie_json_str))
                    
                    # Wait for either task to complete or stop signal
                    await asyncio.gather(receive_task, send_task)
                        
            except websockets.exceptions.ConnectionClosed:
                logger.info("WebSocket connection closed. Attempting to reconnect...")
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"An error occurred: {e}. Attempting to reconnect in 5 seconds...")
                await asyncio.sleep(5)
                    
            finally:
                self.stop_chat()


    def main(self):

        st.markdown("""
            <style>
            .stApp {
                background-color: #ffffff;
            }
            .main-content {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                padding: 2rem 0;
                background-color: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 2rem;
            }
            .input-container {
                margin-bottom: 2rem;
                padding: 1rem;
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
            }
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="header">
                <h1>🌿 Hume</h1>
                <p>A Voice to Guide You Through Panic</p>
            </div>
        """, unsafe_allow_html=True)

        # st.write(st.session_state)

        # Initialize session state
        self.initialize_session_state()
        
        # Setup sidebar components
        self.authenticate()
        self.setup_audio_devices()

        st.sidebar.info("""
            ### Instructions:
            1. Click 'Authenticate' to connect to Hume AI.
            2. Click 'Configure Devices' to select your input and output devices.
            3. Click 'Start Chat' to begin the conversation
            4. Speak clearly into your microphone
            5. The AI assistant's responses will play through your selected output device
            6. Click 'Stop Chat' to end the conversation
            """)

        # Load Lottie animation and audio
        with open("media/hume.json", "r") as f:
            lottie_data = json.load(f)

        lottie_json_str = json.dumps(lottie_data)

        try:
            with open("media/silence.mp3", "rb") as f:
                audio_bytes = f.read()
        except Exception as e:
            st.error("Missing 'media/silence.mp3' file for default audio.")
            return

        start_disabled = not all([
            st.session_state.authenticated,
            st.session_state.is_input_device_selected,
            st.session_state.is_output_device_selected
        ])

        # Display chat status and instructions
        if st.session_state.authenticated:
            st.info(f"Status: {'Connected to Hume AI - Chat Active' if not start_disabled else 'Connected to Hume AI - Chat Inactive'}")
        else:
            st.warning("Please authenticate using your Hume AI credentials in the sidebar")
        

        if(st.session_state.is_output_device_selected and st.session_state.is_input_device_selected):
            st.write("Input Device: ", st.session_state.selected_input_device_name)
            st.write("Output Device: ", st.session_state.selected_output_device_name)

        # Display the animation container
        lottie_audio_visualizer(audio_bytes, lottie_json_str)

        # Create columns for Start and Stop buttons
        col1, col2 = st.columns(2)

        if col1.button("Start Chat", disabled=start_disabled, key="start_button", use_container_width=True, type="secondary"):
            with st.spinner("Started audio chat..."):
                asyncio.run(self.start_audio_stream(lottie_json_str))
        
        # Stop button
        if col2.button("Stop Chat", key="stop_button", use_container_width=True, type="primary"):
            self.stop_chat()
        

if __name__ == "__main__":
    app = StreamlitAudioChat()
    app.main()