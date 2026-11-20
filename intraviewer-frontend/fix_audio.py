import os

with open("src/app/interview/[id]/page.tsx", "r") as f:
    content = f.read()

# Add window.speechSynthesis.cancel() before speaking
old_speak = """  const speak = (text: string) => {
    setIsAiSpeaking(true);
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);"""

new_speak = """  const speak = (text: string) => {
    console.log("AI is speaking:", text);
    setIsAiSpeaking(true);
    const synth = window.speechSynthesis;
    synth.cancel(); // Clear any stuck utterances
    const utterance = new SpeechSynthesisUtterance(text);"""

content = content.replace(old_speak, new_speak)

# Let's also make sure voices are pre-loaded
old_voices = """  const handleUserSpeech = async (text: string) => {"""
new_voices = """  useEffect(() => {
    // Preload voices
    window.speechSynthesis.onvoiceschanged = () => {
      window.speechSynthesis.getVoices();
    };
  }, []);

  const handleUserSpeech = async (text: string) => {"""

content = content.replace(old_voices, new_voices)

with open("src/app/interview/[id]/page.tsx", "w") as f:
    f.write(content)

print("Updated audio code")
