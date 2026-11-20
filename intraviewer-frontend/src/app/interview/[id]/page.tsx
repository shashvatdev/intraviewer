
"use client";

import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiClient } from "@/lib/api/client";
import { Mic, MicOff, Video, VideoOff, Settings, MessageSquare, Users, Info, ShieldAlert } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function InterviewPage() {
  const params = useParams();
  const router = useRouter();
  
  const [session, setSession] = useState<any>(null);
  const [joined, setJoined] = useState(false);
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  
  const [transcript, setTranscript] = useState<any[]>([]);
  const [isAiSpeaking, setIsAiSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [aiTypingText, setAiTypingText] = useState("");
  
  // VAD & Audio Recording
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const silenceTimerRef = useRef<any>(null);
  const forceSilenceTimerRef = useRef<any>(null);
  const vadIntervalRef = useRef<any>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  // Proctoring States
  const [integrityScore, setIntegrityScore] = useState(100);
  const [warnings, setWarnings] = useState<string[]>([]);
  const tabStrikesRef = useRef(0);
  const gracePeriodRef = useRef(true);
  
  const scrollRef = useRef<HTMLDivElement>(null);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);

  // --- PROCTORING ENGINE ---
  const logProctoringEvent = async (type: string, desc: string) => {
    try {
      setWarnings(prev => [desc, ...prev].slice(0, 3));
      const res = await apiClient.post(`/interviews/${params.id}/proctoring-event`, {
        event_type: type, description: desc
      });
      setIntegrityScore(res.data.data.integrity_score);
    } catch(e) {}
  };

  useEffect(() => {
    if (!joined) return;
    
    const handleVisibilityChange = () => {
      if (document.hidden) {
        if (gracePeriodRef.current) return; // Ignore initial focus loss due to camera prompts or fullscreen
        
        tabStrikesRef.current += 1;
        logProctoringEvent("TAB_SWITCH", `Tab switch detected. Strike ${tabStrikesRef.current}/3.`);
        
        const warningVoice = new SpeechSynthesisUtterance(`Warning ${tabStrikesRef.current} of 3. You have switched tabs. We are monitoring this activity and may terminate your session.`);
        window.speechSynthesis.speak(warningVoice);
        
        if (tabStrikesRef.current >= 3) {
           alert("Interview terminated due to multiple proctoring violations.");
           apiClient.post(`/interviews/${params.id}/terminate`).then(() => {
               router.push("/dashboard/candidate/applications");
           }).catch(() => {
               router.push("/dashboard/candidate/applications");
           });
        }
      }
    };
    
    document.addEventListener("visibilitychange", handleVisibilityChange);
    
    if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen().catch(()=>console.log("FS failed"));
    }
    
    // Grace period ends after 3 seconds
    setTimeout(() => { gracePeriodRef.current = false; }, 3000);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [joined, router]);
  
  // --- END PROCTORING ---

  // --- VAD & RECORDING ENGINE ---
  const startRecording = () => {
    if (!videoStream) return;
    setIsListening(true);
    
    const audioTrack = videoStream.getAudioTracks()[0];
    if (!audioTrack) return;
    
    const stream = new MediaStream([audioTrack]);
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    audioChunksRef.current = [];
    
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunksRef.current.push(e.data);
    };
    
    mediaRecorder.onstop = async () => {
      setIsListening(false);
      const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
      
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = async () => {
        const base64Audio = (reader.result as string).split(",")[1];
        await sendAudioToBackend(base64Audio);
      };
    };
    
    mediaRecorder.start();
    
    // Setup VAD
    if (!audioContextRef.current) {
       audioContextRef.current = new AudioContext();
    }
    if (audioContextRef.current.state === "suspended") {
       audioContextRef.current.resume();
    }
    const source = audioContextRef.current.createMediaStreamSource(stream);
    analyserRef.current = audioContextRef.current.createAnalyser();
    source.connect(analyserRef.current);
    
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    
    vadIntervalRef.current = setInterval(() => {
       analyserRef.current?.getByteFrequencyData(dataArray);
       const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
       
       if (average > 15) {
          setIsSpeaking(true);
          // Reset silence timer
          if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
          if (forceSilenceTimerRef.current) clearTimeout(forceSilenceTimerRef.current);
          
          silenceTimerRef.current = setTimeout(() => {
             setIsSpeaking(false);
             stopRecording();
          }, 800); // 1.8s cutoff
       }
    }, 100);
    
    // 7 second absolute silence penalty -> auto submit blank
    forceSilenceTimerRef.current = setTimeout(() => {
       stopRecording();
    }, 7000);
  };
  
  const stopRecording = () => {
     if (vadIntervalRef.current) clearInterval(vadIntervalRef.current);
     if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
     if (forceSilenceTimerRef.current) clearTimeout(forceSilenceTimerRef.current);
     if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
        mediaRecorderRef.current.stop();
     }
  };

  const sendAudioToBackend = async (base64Audio: string) => {
    try {
      const res = await apiClient.post(`/interviews/${params.id}/message`, { audio_base64: base64Audio });
      
      const userText = res.data.data.user_transcribed_text;
      if (userText) {
         setTranscript(prev => [...prev, { role: "user", content: userText }]);
      }
      
      const aiResponse = res.data.data.response;
      const audioBase64 = res.data.data.audio_base64;
      const isCompleted = res.data.data.is_completed;
      
      setTranscript(prev => [...prev, { role: "assistant", content: aiResponse, isCompleted }]);
      
      if (audioBase64) {
         playAiAudio(audioBase64, aiResponse, isCompleted);
      }
    } catch(e) {
      console.error("Backend Error", e);
      startRecording(); // Restart if failed
    }
  };

  const playAiAudio = (audioBase64: string, fullText: string, isCompleted: boolean) => {
    setIsAiSpeaking(true);
    setAiTypingText("");
    
    const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
    currentAudioRef.current = audio;
    
    // Typewriter effect
    let charIndex = 0;
    const typeInterval = setInterval(() => {
       if (charIndex < fullText.length) {
          setAiTypingText(fullText.slice(0, charIndex + 1));
          charIndex++;
       } else {
          clearInterval(typeInterval);
       }
    }, 35);
    
    audio.onended = () => {
      clearInterval(typeInterval);
      setAiTypingText(fullText);
      setIsAiSpeaking(false);
      
      if (isCompleted) {
         setTimeout(() => {
            router.push("/dashboard/candidate/applications");
         }, 3000);
      } else {
         startRecording(); // Start listening immediately!
      }
    };
    
    audio.play().catch(e => {
       console.error("Audio blocked", e);
       setIsAiSpeaking(false);
       clearInterval(typeInterval);
       setAiTypingText(fullText);
       startRecording();
    });
  };

  // --- INIT ENGINE ---
  useEffect(() => {
    apiClient.get(`/interviews/${params.id}`).then(res => {
      setSession(res.data.data);
      if (res.data.data.status === "COMPLETED") {
        setJoined(true);
        setTranscript(res.data.data.transcript);
      }
    });
    
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      .then(stream => {
        setVideoStream(stream);
        if (videoRef.current) videoRef.current.srcObject = stream;
      })
      .catch(err => console.error("Media access denied", err));
      
    return () => {
      if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
      }
      if (currentAudioRef.current) currentAudioRef.current.pause();
      stopRecording();
    };
  }, [params.id]);

  useEffect(() => {
    if (videoRef.current && videoStream) {
      videoRef.current.srcObject = videoStream;
    }
  }, [joined, videoStream]);
  
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [transcript, aiTypingText]);

  const startCall = async () => {
    setJoined(true);
    try {
      const res = await apiClient.post(`/interviews/${params.id}/message`, { message: "" });
      const intro = res.data.data.response;
      setTranscript([{ role: "assistant", content: intro }]);
      if (res.data.data.audio_base64) {
         playAiAudio(res.data.data.audio_base64, intro, false);
      }
    } catch(e) {}
  };
  
  if (!session) return <div className="h-screen flex items-center justify-center text-white">Loading...</div>;

  return (
    <div className="h-screen w-full flex items-center justify-center p-4 sm:p-8 bg-black relative">
      
      {!joined ? (
        <div className="w-full max-w-5xl bg-white text-black rounded-xl overflow-hidden shadow-2xl flex flex-col md:flex-row min-h-[500px]">
          <div className="absolute top-8 left-8 flex items-center gap-2 z-10">
            <div className="bg-[#6B52FF] text-white p-1 rounded font-bold text-xl px-2">α</div>
            <span className="font-bold text-xl text-black">apriora</span>
          </div>
          
          <div className="flex-1 p-12 flex flex-col justify-center border-r border-gray-100">
            <div className="w-full aspect-video bg-gray-900 rounded-xl overflow-hidden relative shadow-inner">
              <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover transform scale-x-[-1]" />
              <div className="absolute bottom-4 left-4 text-white text-sm font-medium drop-shadow-md">
                {session.candidate_name}
              </div>
            </div>
          </div>
          
          <div className="w-[400px] flex flex-col items-center justify-center p-8">
            <h2 className="text-3xl font-semibold mb-8">Ready to join?</h2>
            <div className="w-20 h-20 rounded-full overflow-hidden mb-4 border-2 border-white shadow-md">
              <img src="https://i.pravatar.cc/150?img=47" alt="Alex AI" className="w-full h-full object-cover" />
            </div>
            <p className="text-gray-600 mb-6">Alex is in the call</p>
            <p className="text-xs text-red-500 mb-6 font-medium text-center">Anti-Cheat Enabled: Exiting fullscreen or switching tabs will be recorded.</p>
            <button onClick={startCall} className="bg-[#6B52FF] hover:bg-[#5b45df] text-white px-8 py-3 rounded-full font-medium transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
              Join call
            </button>
          </div>
        </div>
      ) : (
        <div className="w-full max-w-7xl h-full bg-[#1A1C20] rounded-2xl overflow-hidden shadow-2xl flex flex-col relative border-4 border-[#3AE2CE]/30">
          
          <div className="h-10 w-full flex items-center justify-between px-4 bg-black/20 absolute top-0 z-20">
             <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
             </div>
             <div className="flex items-center gap-4 text-xs font-medium">
               {warnings.length > 0 && (
                 <motion.div initial={{opacity:0, y:-10}} animate={{opacity:1, y:0}} className="text-red-400 flex items-center gap-1 bg-red-500/10 px-2 py-1 rounded">
                   <ShieldAlert className="w-3 h-3" /> {warnings[0]}
                 </motion.div>
               )}
               <div className={`px-2 py-1 rounded ${integrityScore > 80 ? 'bg-green-500/20 text-green-400' : integrityScore > 50 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}`}>
                  Integrity Score: {integrityScore}%
               </div>
             </div>
          </div>

          <div className="flex flex-1 pt-10 h-full overflow-hidden p-6 gap-6">
            <div className="flex-1 relative bg-black rounded-xl overflow-hidden shadow-inner">
              <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover transform scale-x-[-1]" />
              
              <motion.div 
                 animate={{ scale: isAiSpeaking ? [1, 1.05, 1] : 1 }}
                 transition={{ repeat: isAiSpeaking ? Infinity : 0, duration: 2 }}
                 className={`absolute bottom-6 right-6 w-32 h-32 rounded-3xl overflow-hidden shadow-2xl border-4 ${isAiSpeaking ? 'border-[#3AE2CE]' : 'border-white/10'} bg-[#2A2D35] flex items-center justify-center p-1`}
              >
                 <img src="https://i.pravatar.cc/150?img=47" alt="Alex AI" className="w-full h-full object-cover rounded-2xl" />
                 <div className="absolute bottom-2 left-2 bg-black/60 px-2 py-0.5 rounded text-xs backdrop-blur-sm">Alex {isAiSpeaking && "..."}</div>
              </motion.div>

              <div className="absolute bottom-6 left-6 text-white/80 text-sm font-medium drop-shadow-md flex items-center gap-2 bg-black/40 px-3 py-1.5 rounded-md backdrop-blur-md">
                 1:16 PM | {session.job_title} Interview
              </div>
              
              {/* VAD Indicator Overlay */}
              {isListening && (
                 <div className="absolute top-6 right-6 flex items-center gap-2 bg-black/60 px-3 py-1.5 rounded-full backdrop-blur-md">
                    <div className={`w-3 h-3 rounded-full ${isSpeaking ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
                    <span className="text-xs font-medium text-white">{isSpeaking ? 'Speaking...' : 'Listening...'}</span>
                 </div>
              )}
            </div>

            <div className="w-[380px] bg-white rounded-xl shadow-lg flex flex-col overflow-hidden text-black h-full relative">
              <div className="p-4 border-b border-gray-100 flex justify-center sticky top-0 bg-white/90 backdrop-blur z-10">
                <h3 className="font-semibold text-gray-800 text-sm uppercase tracking-wider">Live Transcript</h3>
              </div>
              
              <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {transcript.map((msg, i) => {
                  const isLastAi = msg.role === "assistant" && i === transcript.length - 1;
                  const displayContent = (isLastAi && isAiSpeaking) ? aiTypingText : msg.content;
                  
                  return (
                    <div key={i} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
                      {msg.role === "assistant" && <span className="text-xs text-gray-400 mb-1 ml-1">Alex</span>}
                      <div className={`p-3 max-w-[85%] text-sm ${
                        msg.role === "user" 
                          ? "bg-[#6B52FF] text-white rounded-2xl rounded-tr-sm" 
                          : "bg-gray-100 text-gray-800 rounded-2xl rounded-tl-sm"
                      }`}>
                        {displayContent}
                        {isLastAi && isAiSpeaking && <span className="inline-block w-1 h-3 ml-1 bg-gray-400 animate-pulse"></span>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
          
        </div>
      )}
    </div>
  );
}
