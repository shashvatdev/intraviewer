import os

with open("src/app/interview/[id]/page.tsx", "r") as f:
    content = f.read()

old_start = """  const startCall = async () => {
    setJoined(true);
    try {
      const res = await apiClient.post(`/interviews/${params.id}/message`, { message: "" });"""

new_start = """  const startCall = async () => {
    // UNLOCK AUDIO ENGINE SYNCHRONOUSLY
    const synth = window.speechSynthesis;
    const unlockUtterance = new SpeechSynthesisUtterance("");
    synth.speak(unlockUtterance);

    setJoined(true);
    try {
      const res = await apiClient.post(`/interviews/${params.id}/message`, { message: "" });"""

content = content.replace(old_start, new_start)

# Also fix mic/camera always open. 
# "mic camera hamesha khula rahe ga" means they want the toggle buttons removed or disabled during the test?
# Usually anti-cheat forces mic/cam ON. Let's make toggles do nothing or hide them during the call.
# In the controls:
# <button onClick={toggleMic} ...>
# <button onClick={toggleCam} ...>

# Let's disable the ability to turn them off in the in-call screen.

old_controls = """            <div className="flex gap-4">
               <button onClick={toggleMic} className={`w-12 h-12 rounded-full flex items-center justify-center ${micOn ? 'bg-white/10 hover:bg-white/20' : 'bg-red-500 hover:bg-red-600'} transition-colors`}>
                  {micOn ? <Mic className="w-5 h-5"/> : <MicOff className="w-5 h-5"/>}
               </button>
               <button onClick={toggleCam} className={`w-12 h-12 rounded-full flex items-center justify-center ${camOn ? 'bg-white/10 hover:bg-white/20' : 'bg-red-500 hover:bg-red-600'} transition-colors`}>
                  {camOn ? <Video className="w-5 h-5"/> : <VideoOff className="w-5 h-5"/>}
               </button>"""

new_controls = """            <div className="flex gap-4">
               <button className={`w-12 h-12 rounded-full flex items-center justify-center bg-white/10 opacity-50 cursor-not-allowed transition-colors`} title="Mic is locked ON for Proctoring">
                  <Mic className="w-5 h-5"/>
               </button>
               <button className={`w-12 h-12 rounded-full flex items-center justify-center bg-white/10 opacity-50 cursor-not-allowed transition-colors`} title="Camera is locked ON for Proctoring">
                  <Video className="w-5 h-5"/>
               </button>"""
               
content = content.replace(old_controls, new_controls)

with open("src/app/interview/[id]/page.tsx", "w") as f:
    f.write(content)

print("Updated audio unlock & disabled toggles")
