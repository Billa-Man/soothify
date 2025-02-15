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


def lottie_audio_visualizer(audio_bytes: bytes, lottie_json: str):
    """
    Renders a Lottie animation that reacts to the audio's amplitude.
    Audio and animation will loop indefinitely.
    """
    audio_base64 = base64.b64encode(audio_bytes).decode()

    html_code = f"""
    <div id="lottie-container" style="width: 300px; height: 300px; margin: 0 auto 20px auto;"></div>
    <audio id="custom-audio" src="data:audio/mp3;base64,{audio_base64}" controls style="display:none;" loop></audio>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.7.5/lottie.min.js"></script>
    
    <script>
      var lottieData = {lottie_json};
      var anim = lottie.loadAnimation({{
        container: document.getElementById('lottie-container'),
        renderer: 'svg',
        loop: true,
        autoplay: false,
        animationData: lottieData
      }});
      
      var audioElement = document.getElementById('custom-audio');
      var AudioContext = window.AudioContext || window.webkitAudioContext;
      var audioCtx = new AudioContext();
      var analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      var bufferLength = analyser.frequencyBinCount;
      var dataArray = new Uint8Array(bufferLength);
      
      var source = audioCtx.createMediaElementSource(audioElement);
      source.connect(analyser);
      analyser.connect(audioCtx.destination);
      
      function animate() {{
          requestAnimationFrame(animate);
          analyser.getByteFrequencyData(dataArray);
          var sum = 0;
          for (var i = 0; i < bufferLength; i++) {{
              sum += dataArray[i];
          }}
          var average = sum / bufferLength;
          var scale = 1 + average / 256;
          document.getElementById('lottie-container').style.transform = 'scale(' + scale + ')';
      }}
      
      audioElement.onplay = function() {{
          if (audioCtx.state === 'suspended') {{
              audioCtx.resume();
          }}
          anim.play();
          animate();
      }};
      
      // Remove the onended handler since we want continuous playback
      
      audioElement.play().catch(function(err) {{
          console.log("Autoplay failed:", err);
      }});
    </script>
    """
    components.html(html_code, height=320)
    
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
        if 'chat_active' not in st.session_state:
            st.session_state.chat_active = False
        if 'stop_chat' not in st.session_state:
            st.session_state.stop_chat = False

    def get_audio_devices(self):
        """Get available audio input and output devices"""
        return AudioDevices.list_audio_devices(self.pyaudio)

    def authenticate(self):
        """
        Handle authentication with Hume AI
        """

        st.sidebar.header("Authentication")
        
        # Load environment variables
        api_key = settings.HUME_API_KEY or st.sidebar.text_input("Hume API Key", type="password")
        secret_key = settings.HUME_SECRET_KEY or st.sidebar.text_input("Hume Secret Key", type="password")
        
        if st.sidebar.button("Authenticate"):
            if api_key and secret_key:
                try:
                    authenticator = Authenticator(api_key, secret_key)
                    access_token = authenticator.fetch_access_token()
                    st.session_state.access_token = access_token
                    st.session_state.authenticated = True
                    st.sidebar.success("Authentication successful!")
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
        selected_input = input_device_names[0]
        
        # Output device selection
        output_device_names = [f"{name} ({idx})" for idx, name, _ in output_devices]
        selected_output = st.sidebar.selectbox(
            "Select Output Device",
            output_device_names,
            index=0 if output_device_names else None
        )
        selected_output = output_device_names[0]
        
        if st.sidebar.button("Configure Devices"):
            if selected_input and selected_output:
                input_idx = int(selected_input.split("(")[-1].strip(")"))
                output_idx = int(selected_output.split("(")[-1].strip(")"))
                
                # Find the selected input device's sample rate
                input_device = next((device for device in input_devices if device[0] == input_idx), None)
                if input_device:
                    sample_rate = input_device[2]
                    
                    # Store selected devices in session state
                    st.session_state.selected_input_device = (input_idx, sample_rate)
                    st.session_state.selected_output_device = output_idx
                    
                    st.sidebar.success("Audio devices configured successfully!")
                else:
                    st.sidebar.error("Failed to get input device information")
            else:
                st.sidebar.error("Please select both input and output devices")

    async def start_audio_stream(self, lottie_json_str):
        """
        Start the audio stream with WebSocket connection
        """
        if not all([
            st.session_state.authenticated,
            st.session_state.selected_input_device,
            st.session_state.selected_output_device
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

        try:
            while not st.session_state.stop_chat:
                try:
                    async with websockets.connect(socket_url) as socket:
                        print("Connected to WebSocket")
                        send_task = asyncio.create_task(
                            Connection._send_audio_data(
                                socket,
                                self.audio_stream,
                                sample_rate,
                                SAMPLE_WIDTH,
                                CHANNELS,
                                CHUNK_SIZE,
                            )
                        )
                        receive_task = asyncio.create_task(
                            Connection._receive_audio_data(socket, lottie_json_str)
                        )
                        
                        # Wait for either task to complete or stop signal
                        done, pending = await asyncio.wait(
                            [send_task, receive_task],
                            return_when=asyncio.FIRST_COMPLETED
                        )
                        
                        # Cancel pending tasks
                        for task in pending:
                            task.cancel()
                            
                        if st.session_state.stop_chat:
                            break
                            
                except websockets.exceptions.ConnectionClosed:
                    if st.session_state.stop_chat:
                        break
                    print("WebSocket connection closed. Attempting to reconnect...")
                    await asyncio.sleep(5)
                    
        finally:
            # Clean up resources
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
            st.session_state.chat_active = False
            st.session_state.stop_chat = False

    def stop_audio_stream(self):
        """Stop the audio stream and WebSocket connection"""
        st.session_state.stop_chat = True
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None

    def start_chat(self):
        """Set chat as active and trigger rerun"""
        st.session_state.chat_active = True
        st.session_state.stop_chat = False

    def stop_chat(self):
        """Set chat as inactive and trigger rerun"""
        st.session_state.chat_active = False
        st.session_state.stop_chat = True
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None

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


        # """Main Streamlit application"""
        # st.title("Hume AI Voice Chat")
        
        # Initialize session state
        self.initialize_session_state()
        
        # Setup sidebar components
        self.authenticate()
        self.setup_audio_devices()

        with open("media/hume.json", "r") as f:
            lottie_data = json.load(f)
        lottie_json_str = json.dumps(lottie_data)

        try:
            with open("media/silence.mp3", "rb") as f:
                audio_bytes = f.read()
        except Exception as e:
            st.error("Missing 'media/silence.mp3' file for default audio.")
            return

        # Display the animation container
        lottie_audio_visualizer(audio_bytes, lottie_json_str)
        
        # Main chat interface
        st.header("Chat Interface")
        
        # Create columns for Start and Stop buttons
        col1, col2 = st.columns(2)
        
        # Start button
        # start_disabled = not all([
        #     st.session_state.authenticated,
        #     st.session_state.selected_input_device,
        #     st.session_state.selected_output_device
        # ]) or st.session_state.chat_active

        start_disabled = False
        
        if col1.button("Start Chat", disabled=start_disabled, key="start_button"):
            self.start_chat()
            with st.spinner("Started audio chat..."):
                asyncio.run(self.start_audio_stream(lottie_json_str))
        
        # Stop button
        if col2.button("Stop Chat", key="stop_button"):
            self.stop_chat()
        
        # Display chat status and instructions
        # if st.session_state.authenticated:
        st.info(f"Status: {'Connected to Hume AI - Chat Active' if st.session_state.chat_active else 'Connected to Hume AI - Chat Inactive'}")
        st.sidebar.info("""
        ### Instructions:
        1. Click 'Start Chat' to begin the conversation
        2. Speak clearly into your microphone
        3. The AI assistant's responses will play through your selected output device
        4. Click 'Stop Chat' to end the conversation
        """)
        # else:
        #     st.warning("Please authenticate using your Hume AI credentials in the sidebar")


if __name__ == "__main__":
    app = StreamlitAudioChat()
    app.main()