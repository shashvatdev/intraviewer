import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

interview_layout = """
export default function InterviewLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#111111] text-white overflow-hidden">
      {children}
    </div>
  );
}
"""

interview_page = """
"use client";

import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import { apiClient } from "@/lib/api/client";
import { Mic, MicOff, Video, VideoOff, Settings, MessageSquare, Users, Info } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function InterviewPage() {
  const params = useParams();
  const [session, setSession] = useState<any>(null);
  const [joined, setJoined] = useState(false);
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  
  const [micOn, setMicOn] = useState(true);
  const [camOn, setCamOn] = useState(true);
  const [transcript, setTranscript] = useState<any[]>([]);
  const [isAiSpeaking, setIsAiSpeaking] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);
  const [isListening, setIsListening] = useState(false);
  
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    apiClient.get(`/interviews/${params.id}`).then(res => {
      setSession(res.data.data);
      if (res.data.data.status === "COMPLETED") {
        setJoined(true);
        setTranscript(res.data.data.transcript);
      }
    });
    
    // Setup camera
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      .then(stream => {
        setVideoStream(stream);
        if (videoRef.current) videoRef.current.srcObject = stream;
      })
      .catch(err => console.error("Media access denied", err));
      
    // Setup speech recognition
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
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
    }
    
    return () => {
      if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
      }
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
  }, [transcript]);

  const speak = (text: string) => {
    setIsAiSpeaking(true);
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    // Find a good female voice to match the "Alex" persona
    const voices = synth.getVoices();
    const femaleVoice = voices.find(v => v.name.includes("Female") || v.name.includes("Samantha") || v.name.includes("Google US English"));
    if (femaleVoice) utterance.voice = femaleVoice;
    
    utterance.rate = 1.0;
    utterance.onend = () => {
      setIsAiSpeaking(false);
      // Automatically start listening after AI finishes
      if (recognition) {
        try {
          recognition.start();
          setIsListening(true);
        } catch(e) {}
      }
    };
    synth.speak(utterance);
  };

  const handleUserSpeech = async (text: string) => {
    // Optimistically add to UI
    setTranscript(prev => [...prev, { role: "user", content: text }]);
    
    try {
      const res = await apiClient.post(`/interviews/${params.id}/message`, { message: text });
      const aiResponse = res.data.data.response;
      
      setTranscript(prev => [...prev, { role: "assistant", content: aiResponse }]);
      speak(aiResponse);
      
    } catch(e) {
      console.error(e);
    }
  };

  const startCall = async () => {
    setJoined(true);
    try {
      const res = await apiClient.post(`/interviews/${params.id}/message`, { message: "" });
      const intro = res.data.data.response;
      setTranscript([{ role: "assistant", content: intro }]);
      // Wait a moment for UI to render then speak
      setTimeout(() => speak(intro), 500);
    } catch(e) {}
  };
  
  const toggleMic = () => {
    if (videoStream) {
      videoStream.getAudioTracks().forEach(t => t.enabled = !micOn);
      setMicOn(!micOn);
    }
  };
  
  const toggleCam = () => {
    if (videoStream) {
      videoStream.getVideoTracks().forEach(t => t.enabled = !camOn);
      setCamOn(!camOn);
    }
  };

  if (!session) return <div className="h-screen flex items-center justify-center text-white">Loading...</div>;

  return (
    <div className="h-screen w-full flex items-center justify-center p-4 sm:p-8 bg-black relative">
      
      {!joined ? (
        // PRE-CALL SCREEN
        <div className="w-full max-w-5xl bg-white text-black rounded-xl overflow-hidden shadow-2xl flex flex-col md:flex-row min-h-[500px]">
          {/* Brand header simulated */}
          <div className="absolute top-8 left-8 flex items-center gap-2 z-10">
            <div className="bg-[#6B52FF] text-white p-1 rounded font-bold text-xl px-2">α</div>
            <span className="font-bold text-xl text-black">apriora</span>
          </div>
          
          {/* Left: Video Preview */}
          <div className="flex-1 p-12 flex flex-col justify-center border-r border-gray-100">
            <div className="w-full aspect-video bg-gray-900 rounded-xl overflow-hidden relative shadow-inner">
              {camOn ? (
                <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover transform scale-x-[-1]" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-500">Camera Off</div>
              )}
              <div className="absolute bottom-4 left-4 text-white text-sm font-medium drop-shadow-md">
                {session.candidate_name}
              </div>
            </div>
            
            <div className="flex justify-center gap-6 mt-6 text-sm text-gray-600">
              <button onClick={toggleCam} className="flex items-center gap-2 hover:text-black">
                {camOn ? <Video className="w-4 h-4"/> : <VideoOff className="w-4 h-4"/>} FaceTime HD Camera
              </button>
              <button onClick={toggleMic} className="flex items-center gap-2 hover:text-black">
                {micOn ? <Mic className="w-4 h-4"/> : <MicOff className="w-4 h-4"/>} AirPods
              </button>
              <button className="flex items-center gap-2 hover:text-black">
                <Settings className="w-4 h-4"/>
              </button>
            </div>
          </div>
          
          {/* Right: Join Info */}
          <div className="w-[400px] flex flex-col items-center justify-center p-8">
            <h2 className="text-3xl font-semibold mb-8">Ready to join?</h2>
            <div className="w-20 h-20 rounded-full overflow-hidden mb-4 border-2 border-white shadow-md">
              <img src="https://i.pravatar.cc/150?img=47" alt="Alex AI" className="w-full h-full object-cover" />
            </div>
            <p className="text-gray-600 mb-6">Alex is in the call</p>
            <button onClick={startCall} className="bg-[#6B52FF] hover:bg-[#5b45df] text-white px-8 py-3 rounded-full font-medium transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
              Join call
            </button>
          </div>
        </div>
      ) : (
        // IN-CALL SCREEN
        <div className="w-full max-w-7xl h-full bg-[#1A1C20] rounded-2xl overflow-hidden shadow-2xl flex flex-col relative border-4 border-[#3AE2CE]/30">
          
          {/* Top Bar simulated */}
          <div className="h-10 w-full flex items-center justify-between px-4 bg-black/20 absolute top-0 z-20">
             <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
             </div>
          </div>

          <div className="flex flex-1 pt-10 h-full overflow-hidden p-6 gap-6">
            {/* Left: Main Video Container */}
            <div className="flex-1 relative bg-black rounded-xl overflow-hidden shadow-inner">
              {camOn ? (
                 <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover transform scale-x-[-1]" />
              ) : (
                 <div className="w-full h-full flex items-center justify-center text-gray-500">Camera Off</div>
              )}
              
              {/* Floating AI Avatar Bottom Right */}
              <motion.div 
                 animate={{ scale: isAiSpeaking ? [1, 1.05, 1] : 1 }}
                 transition={{ repeat: isAiSpeaking ? Infinity : 0, duration: 2 }}
                 className={`absolute bottom-6 right-6 w-32 h-32 rounded-3xl overflow-hidden shadow-2xl border-4 ${isAiSpeaking ? 'border-[#3AE2CE]' : 'border-white/10'} bg-[#2A2D35] flex items-center justify-center p-1`}
              >
                 <img src="https://i.pravatar.cc/150?img=47" alt="Alex AI" className="w-full h-full object-cover rounded-2xl" />
                 <div className="absolute bottom-2 left-2 bg-black/60 px-2 py-0.5 rounded text-xs backdrop-blur-sm">Alex {isAiSpeaking && "..."}</div>
              </motion.div>

              {/* Bottom Left Info */}
              <div className="absolute bottom-6 left-6 text-white/80 text-sm font-medium drop-shadow-md flex items-center gap-2 bg-black/40 px-3 py-1.5 rounded-md backdrop-blur-md">
                 1:16 PM | {session.job_title} Interview
              </div>
            </div>

            {/* Right: Live Transcript */}
            <div className="w-[380px] bg-white rounded-xl shadow-lg flex flex-col overflow-hidden text-black h-full relative">
              <div className="p-4 border-b border-gray-100 flex justify-center sticky top-0 bg-white/90 backdrop-blur z-10">
                <h3 className="font-semibold text-gray-800 text-sm uppercase tracking-wider">Live Transcript</h3>
              </div>
              
              <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {transcript.map((msg, i) => (
                  <div key={i} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
                    {msg.role === "assistant" && <span className="text-xs text-gray-400 mb-1 ml-1">Alex</span>}
                    <div className={`p-3 max-w-[85%] text-sm ${
                      msg.role === "user" 
                        ? "bg-[#6B52FF] text-white rounded-2xl rounded-tr-sm" 
                        : "bg-gray-100 text-gray-800 rounded-2xl rounded-tl-sm"
                    }`}>
                      {msg.content}
                    </div>
                  </div>
                ))}
                {isListening && (
                   <div className="flex flex-col items-end">
                     <div className="p-3 bg-[#6B52FF]/20 text-[#6B52FF] rounded-2xl rounded-tr-sm text-sm animate-pulse">
                        Listening...
                     </div>
                   </div>
                )}
              </div>
            </div>
          </div>

          {/* Bottom Control Bar */}
          <div className="h-16 flex items-center justify-between px-8 bg-[#1A1C20] border-t border-white/5">
            <div></div>
            <div className="flex gap-4">
               <button onClick={toggleMic} className={`w-12 h-12 rounded-full flex items-center justify-center ${micOn ? 'bg-white/10 hover:bg-white/20' : 'bg-red-500 hover:bg-red-600'} transition-colors`}>
                  {micOn ? <Mic className="w-5 h-5"/> : <MicOff className="w-5 h-5"/>}
               </button>
               <button onClick={toggleCam} className={`w-12 h-12 rounded-full flex items-center justify-center ${camOn ? 'bg-white/10 hover:bg-white/20' : 'bg-red-500 hover:bg-red-600'} transition-colors`}>
                  {camOn ? <Video className="w-5 h-5"/> : <VideoOff className="w-5 h-5"/>}
               </button>
               <button className="w-12 h-12 rounded-full flex items-center justify-center bg-white/10 hover:bg-white/20 transition-colors">
                  <Info className="w-5 h-5"/>
               </button>
               <button className="w-12 h-12 rounded-full flex items-center justify-center bg-white/10 hover:bg-white/20 transition-colors relative">
                  <Users className="w-5 h-5"/>
                  <span className="absolute -top-1 -right-1 bg-white text-black text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold">2</span>
               </button>
               <button className="w-12 h-12 rounded-full flex items-center justify-center bg-white/10 hover:bg-white/20 transition-colors">
                  <MessageSquare className="w-5 h-5"/>
               </button>
               <button onClick={() => window.location.href="/dashboard/candidate/applications"} className="px-6 h-12 rounded-full flex items-center justify-center bg-red-500 hover:bg-red-600 font-medium transition-colors ml-4">
                  End Interview
               </button>
            </div>
            <div></div>
          </div>
          
        </div>
      )}
    </div>
  );
}
"""

write_file("src/app/interview/layout.tsx", interview_layout)
write_file("src/app/interview/[id]/page.tsx", interview_page)

