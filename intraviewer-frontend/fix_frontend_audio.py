import os

with open("src/app/interview/[id]/page.tsx", "r") as f:
    content = f.read()

# Replace speak function with Audio API playback
old_speak = """  const speak = (text: string) => {
    console.log("AI is speaking:", text);
    setIsAiSpeaking(true);
    
    if (!window.speechSynthesis) {
      console.warn("SpeechSynthesis not supported.");
      setIsAiSpeaking(false);
      return;
    }
    
    const synth = window.speechSynthesis;
    synth.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    const voices = synth.getVoices();
    const femaleVoice = voices.find(v => v.name.includes("Female") || v.name.includes("Samantha") || v.name.includes("Google US English"));
    if (femaleVoice) utterance.voice = femaleVoice;
    
    utterance.onend = () => {
      setIsAiSpeaking(false);
    };
    
    utterance.onerror = (e) => {
      console.error("Speech error", e);
      setIsAiSpeaking(false);
    };
    
    synth.speak(utterance);
  };"""

new_speak = """  const speak = (audioBase64: string) => {
    if (!audioBase64) {
      console.warn("No audio data received.");
      return;
    }
    
    setIsAiSpeaking(true);
    const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
    
    audio.onended = () => {
      setIsAiSpeaking(false);
    };
    
    audio.onerror = (e) => {
      console.error("Audio playback error", e);
      setIsAiSpeaking(false);
    };
    
    audio.play().catch(e => {
      console.error("Browser blocked audio play:", e);
      setIsAiSpeaking(false);
    });
  };"""

content = content.replace(old_speak, new_speak)

# Update handleUserSpeech
old_handle = """      setTranscript(prev => [...prev, { role: "assistant", content: aiResponse }]);
      speak(aiResponse);"""

new_handle = """      setTranscript(prev => [...prev, { role: "assistant", content: aiResponse }]);
      if (res.data.data.audio_base64) {
        speak(res.data.data.audio_base64);
      }"""

content = content.replace(old_handle, new_handle)

# Update startCall
old_start = """      setTranscript([{ role: "assistant", content: intro }]);
      // The speak function will automatically start listening when it finishes!
      setTimeout(() => speak(intro), 500);"""

new_start = """      setTranscript([{ role: "assistant", content: intro }]);
      if (res.data.data.audio_base64) {
        setTimeout(() => speak(res.data.data.audio_base64), 500);
      }"""

content = content.replace(old_start, new_start)

# Remove silent audio unlock hack as it's not needed for HTML Audio element
old_unlock = """  const startCall = async () => {
    const synth = window.speechSynthesis;
    synth.speak(new SpeechSynthesisUtterance(""));"""

new_unlock = """  const startCall = async () => {"""
content = content.replace(old_unlock, new_unlock)

with open("src/app/interview/[id]/page.tsx", "w") as f:
    f.write(content)

print("Updated frontend for MP3 audio")
