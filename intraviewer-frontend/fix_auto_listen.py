import os

with open("src/app/interview/[id]/page.tsx", "r") as f:
    content = f.read()

# Make SpeechRecognition continuous and robust auto-restarting
old_rec_setup = """    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-US';
      
      rec.onresult = (event: any) => {
        const text = event.results[0][0].transcript;
        handleUserSpeech(text);
      };
      
      rec.onend = () => setIsListening(false);
      setRecognition(rec);
    }"""

new_rec_setup = """    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-US';
      
      rec.onresult = (event: any) => {
        const text = event.results[event.results.length - 1][0].transcript;
        if (text.trim().length > 0) {
           handleUserSpeech(text);
        }
      };
      
      rec.onerror = (e: any) => {
        console.error("Speech Recognition Error:", e.error);
        if (e.error !== 'no-speech') {
           setIsListening(false);
        }
      };

      rec.onend = () => {
        // If AI is not speaking and we are in the call, it should ideally keep listening.
        // We handle restarting in a generic interval or explicit calls.
        setIsListening(false);
      };
      
      setRecognition(rec);
    }"""

content = content.replace(old_rec_setup, new_rec_setup)


old_speak = """    utterance.onend = () => {
      setIsAiSpeaking(false);
    };
    
    utterance.onerror = (e) => {
      console.error("Speech error", e);
      setIsAiSpeaking(false);
    };"""

new_speak = """    utterance.onend = () => {
      setIsAiSpeaking(false);
      // Auto-start listening after AI finishes speaking
      if (recognition) {
        try {
          recognition.start();
          setIsListening(true);
        } catch(e) {}
      }
    };
    
    utterance.onerror = (e) => {
      console.error("Speech error", e);
      setIsAiSpeaking(false);
      // Auto-start listening even on error
      if (recognition) {
        try {
          recognition.start();
          setIsListening(true);
        } catch(e) {}
      }
    };"""

content = content.replace(old_speak, new_speak)

old_handle = """  const handleUserSpeech = async (text: string) => {
    setTranscript(prev => [...prev, { role: "user", content: text }]);
    
    try {
      const res = await apiClient.post(`/interviews/${params.id}/message`, { message: text });"""

new_handle = """  const handleUserSpeech = async (text: string) => {
    // Stop listening while AI thinks/speaks
    if (recognition) {
      try { recognition.stop(); } catch(e) {}
    }
    
    setTranscript(prev => [...prev, { role: "user", content: text }]);
    
    try {
      const res = await apiClient.post(`/interviews/${params.id}/message`, { message: text });"""

content = content.replace(old_handle, new_handle)

# We also need to auto-start listening when the call is joined and the intro is fetched
old_start = """  const startCall = async () => {
    // UNLOCK AUDIO ENGINE SYNCHRONOUSLY
    const synth = window.speechSynthesis;
    const unlockUtterance = new SpeechSynthesisUtterance("");
    synth.speak(unlockUtterance);

    setJoined(true);
    try {
      const res = await apiClient.post(`/interviews/${params.id}/message`, { message: "" });
      const intro = res.data.data.response;
      setTranscript([{ role: "assistant", content: intro }]);
      setTimeout(() => speak(intro), 500);
    } catch(e) {}
  };"""

new_start = """  const startCall = async () => {
    const synth = window.speechSynthesis;
    synth.speak(new SpeechSynthesisUtterance(""));

    setJoined(true);
    try {
      const res = await apiClient.post(`/interviews/${params.id}/message`, { message: "" });
      const intro = res.data.data.response;
      setTranscript([{ role: "assistant", content: intro }]);
      // The speak function will automatically start listening when it finishes!
      setTimeout(() => speak(intro), 500);
    } catch(e) {
      console.error(e);
      // Fallback start listening if API fails
      if (recognition) {
        try { recognition.start(); setIsListening(true); } catch(err) {}
      }
    }
  };"""

content = content.replace(old_start, new_start)


with open("src/app/interview/[id]/page.tsx", "w") as f:
    f.write(content)

print("Updated strict auto-listening logic")
