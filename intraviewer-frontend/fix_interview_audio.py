import os

with open("src/app/interview/[id]/page.tsx", "r") as f:
    content = f.read()

# Add chat input state
if "const [chatText, setChatText] = useState" not in content:
    content = content.replace(
        "const [isListening, setIsListening] = useState(false);",
        "const [isListening, setIsListening] = useState(false);\n  const [chatText, setChatText] = useState('');"
    )

# Fix speak and handleUserSpeech logic to be foolproof
old_speak = """  const speak = (text: string) => {
    console.log("AI is speaking:", text);
    setIsAiSpeaking(true);
    const synth = window.speechSynthesis;
    synth.cancel(); // Clear any stuck utterances
    const utterance = new SpeechSynthesisUtterance(text);
    const voices = synth.getVoices();
    const femaleVoice = voices.find(v => v.name.includes("Female") || v.name.includes("Samantha") || v.name.includes("Google US English"));
    if (femaleVoice) utterance.voice = femaleVoice;
    
    utterance.rate = 1.0;
    utterance.onend = () => {
      setIsAiSpeaking(false);
      if (recognition) {
        try {
          recognition.start();
          setIsListening(true);
        } catch(e) {}
      }
    };
    synth.speak(utterance);
  };"""

new_speak = """  const speak = (text: string) => {
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
  };

  const manualToggleListen = () => {
    if (!recognition) return;
    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      try {
        recognition.start();
        setIsListening(true);
      } catch (e) {
        console.error(e);
      }
    }
  };

  const submitChat = () => {
    if (!chatText.trim()) return;
    const text = chatText;
    setChatText('');
    handleUserSpeech(text);
  };"""

content = content.replace(old_speak, new_speak)


old_controls = """            <div className="flex gap-4">
               <button className={`w-12 h-12 rounded-full flex items-center justify-center bg-white/10 opacity-50 cursor-not-allowed transition-colors`} title="Mic is locked ON for Proctoring">
                  <Mic className="w-5 h-5"/>
               </button>"""

new_controls = """            <div className="flex gap-4">
               <button onClick={manualToggleListen} className={`w-12 h-12 rounded-full flex items-center justify-center ${isListening ? 'bg-green-500 hover:bg-green-600 animate-pulse' : 'bg-white/10 hover:bg-white/20'} transition-colors`} title="Click to talk">
                  {isListening ? <Mic className="w-5 h-5 text-white"/> : <MicOff className="w-5 h-5"/>}
               </button>"""

content = content.replace(old_controls, new_controls)


old_transcript_box = """              <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {transcript.map((msg, i) => ("""

new_transcript_box = """              <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {transcript.map((msg, i) => ("""

content = content.replace(old_transcript_box, new_transcript_box)


old_bottom_transcript = """                {isListening && (
                   <div className="flex flex-col items-end">
                     <div className="p-3 bg-[#6B52FF]/20 text-[#6B52FF] rounded-2xl rounded-tr-sm text-sm animate-pulse">
                        Listening...
                     </div>
                   </div>
                )}
              </div>
            </div>"""

new_bottom_transcript = """                {isListening && (
                   <div className="flex flex-col items-end">
                     <div className="p-3 bg-[#6B52FF]/20 text-[#6B52FF] rounded-2xl rounded-tr-sm text-sm animate-pulse">
                        Listening...
                     </div>
                   </div>
                )}
              </div>
              <div className="p-4 border-t border-gray-100 bg-gray-50 flex gap-2">
                 <input 
                   type="text" 
                   value={chatText} 
                   onChange={(e) => setChatText(e.target.value)}
                   onKeyDown={(e) => e.key === 'Enter' && submitChat()}
                   placeholder="Type to reply if mic fails..." 
                   className="flex-1 bg-white border border-gray-200 rounded-full px-4 py-2 text-sm focus:outline-none focus:border-[#6B52FF] text-black"
                 />
                 <button onClick={submitChat} className="w-10 h-10 rounded-full bg-[#6B52FF] text-white flex items-center justify-center flex-shrink-0">
                   <MessageSquare className="w-4 h-4" />
                 </button>
              </div>
            </div>"""

content = content.replace(old_bottom_transcript, new_bottom_transcript)

with open("src/app/interview/[id]/page.tsx", "w") as f:
    f.write(content)

print("Updated fallback audio controls and manual chat")
