import os

with open("src/app/interview/[id]/page.tsx", "r") as f:
    content = f.read()

# Add a grace period ref
if "const gracePeriodRef = useRef(true);" not in content:
    content = content.replace(
        "const tabStrikesRef = useRef(0);",
        "const tabStrikesRef = useRef(0);\n  const gracePeriodRef = useRef(true);"
    )

old_vis = """    const handleVisibilityChange = () => {
      if (document.hidden) {
        tabStrikesRef.current += 1;
        logProctoringEvent("TAB_SWITCH", `Tab switch detected. Strike ${tabStrikesRef.current}/3.`);
        
        const warningVoice = new SpeechSynthesisUtterance(`Warning ${tabStrikesRef.current} of 3. You have switched tabs. We are monitoring this activity and may terminate your session.`);
        window.speechSynthesis.speak(warningVoice);
        
        if (tabStrikesRef.current >= 3) {
           alert("Interview terminated due to multiple proctoring violations.");
           router.push("/dashboard/candidate/applications");
        }
      }
    };"""

new_vis = """    const handleVisibilityChange = () => {
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
    };"""

content = content.replace(old_vis, new_vis)

old_fs = """    if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen().catch(()=>console.log("FS failed"));
    }

    return () => {"""

new_fs = """    if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen().catch(()=>console.log("FS failed"));
    }
    
    // Grace period ends after 3 seconds
    setTimeout(() => { gracePeriodRef.current = false; }, 3000);

    return () => {"""

content = content.replace(old_fs, new_fs)

with open("src/app/interview/[id]/page.tsx", "w") as f:
    f.write(content)

print("Updated frontend proctoring logic")
