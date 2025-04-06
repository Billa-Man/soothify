import base64
import streamlit.components.v1 as components

def lottie_audio_visualizer(audio_bytes: bytes, lottie_json: str):
    """
    Renders a Lottie animation that reacts to the audio's amplitude.
    """
    # Convert audio bytes to a Base64 string
    audio_base64 = base64.b64encode(audio_bytes).decode()
    
    # Build the HTML/JavaScript code.
    html_code = f"""
    <div id="lottie-container" style="
            width: 300px;
            height: 300px;
            margin: 0 auto 20px auto;
        ">
    </div>
    <!-- Hidden audio element -->
    <audio id="custom-audio" src="data:audio/mp3;base64,{audio_base64}" controls style="display:none;"></audio>
    
    <!-- Include Lottie-web -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.7.5/lottie.min.js"></script>
    
    <script>
      var lottieData = {lottie_json};
      var anim = lottie.loadAnimation({{
        container: document.getElementById('lottie-container'),
        renderer: 'svg',
        loop: true,
        autoplay: true,
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
          var scale = 0.9 + average / 256;
          document.getElementById('lottie-container').style.transform = 'scale(' + scale + ')';
      }}
      
      audioElement.onplay = function() {{
          if (audioCtx.state === 'suspended') {{
              audioCtx.resume();
          }}
          animate();
      }};
      
      audioElement.play().catch(function(err) {{
          console.log("Autoplay failed:", err);
      }});
    </script>
    """
    components.html(html_code, height=320)