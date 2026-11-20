
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { apiClient } from "@/lib/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useForm } from "react-hook-form";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, CircleDashed, UploadCloud, FileText, Bot, Settings2 } from "lucide-react";

export default function CreateJobPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [jobId, setJobId] = useState<string | null>(null);
  
  // States for steps
  const [uploadMethod, setUploadMethod] = useState<'FILE'|'TEXT'>('FILE');
  const [jdFile, setJdFile] = useState<File|null>(null);
  const [jdText, setJdText] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [blueprint, setBlueprint] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  
  const formDetails = useForm({
    defaultValues: {
      title: "", department: "", ctc_min: "", ctc_max: "",
      location: "", deadline: ""
    }
  });

  const onDetailsSubmit = async (data: any) => {
    try {
      if (!data.title) {
        toast.error("Job title is required");
        return;
      }
      let payload = { ...data };
      if (data.deadline) {
        payload.deadline = new Date(data.deadline).toISOString();
      }
      
      const res = await apiClient.post("/jobs", payload);
      setJobId(res.data.data.job_id);
      setStep(2);
    } catch (e: any) {
      toast.error(e.response?.data?.message || "Failed to create job");
    }
  };

  const handleJdSubmit = async () => {
    if (!jobId) return;
    try {
      if (uploadMethod === 'FILE') {
        if (!jdFile) { toast.error("Select a file"); return; }
        const formData = new FormData();
        formData.append("file", jdFile);
        await apiClient.post(`/jobs/${jobId}/jd/upload`, formData, {
          headers: { "Content-Type": "multipart/form-data" }
        });
      } else {
        if (!jdText) { toast.error("Paste JD text"); return; }
        await apiClient.post(`/jobs/${jobId}/jd/text`, { raw_text: jdText });
      }
      
      setStep(3);
      startAnalysis();
    } catch (e: any) {
      toast.error(e.response?.data?.message || "Failed to parse JD");
    }
  };

  const startAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      await apiClient.post(`/jobs/${jobId}/jd/analyze`);
      const res = await apiClient.get(`/jobs/${jobId}`);
      setBlueprint(res.data.data.blueprint);
      setAnalysis(res.data.data.analysis);
      setStep(4);
    } catch (e: any) {
      toast.error("AI Analysis failed. Please try again.");
      setStep(2);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleBlueprintSave = async () => {
    try {
      await apiClient.put(`/jobs/${jobId}/blueprint`, {
        estimated_duration: blueprint.estimated_duration,
        similarity_threshold: blueprint.similarity_threshold,
        evaluation_weights: blueprint.evaluation_weights
      });
      setStep(5);
    } catch (e: any) {
      toast.error(e.response?.data?.message || "Failed to update blueprint");
    }
  };

  const handlePublish = async () => {
    try {
      await apiClient.post(`/jobs/${jobId}/publish`);
      toast.success("Job published successfully!");
      router.push("/dashboard/company/jobs");
    } catch(e: any) {
      toast.error("Failed to publish");
    }
  };

  const steps = [
    { num: 1, label: "Details" },
    { num: 2, label: "JD" },
    { num: 3, label: "Analysis" },
    { num: 4, label: "Blueprint" },
    { num: 5, label: "Publish" }
  ];

  return (
    <div className="max-w-3xl mx-auto py-8">
      <div className="mb-8">
        <h2 className="text-2xl font-semibold tracking-tight uppercase">Create New Job</h2>
        <div className="flex items-center gap-2 mt-6 text-sm font-medium text-muted-foreground uppercase tracking-wider overflow-x-auto pb-2">
          {steps.map((s, i) => (
            <div key={s.num} className={`flex items-center gap-2 ${step >= s.num ? "text-primary" : ""}`}>
              <span>{s.num.toString().padStart(2, '0')} {s.label}</span>
              {i < steps.length - 1 && <span className="text-border mx-2">───</span>}
            </div>
          ))}
        </div>
      </div>

      <div className="bg-background border border-border rounded-lg p-6 min-h-[400px]">
        <AnimatePresence mode="wait">
          
          {/* STEP 1 */}
          {step === 1 && (
            <motion.div key="step1" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <form onSubmit={formDetails.handleSubmit(onDetailsSubmit)} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input label="Job Title *" placeholder="Software Engineer" {...formDetails.register("title")} />
                  <Input label="Department" placeholder="Engineering" {...formDetails.register("department")} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Input label="Min CTC (LPA)" placeholder="6" {...formDetails.register("ctc_min")} />
                  <Input label="Max CTC (LPA)" placeholder="10" {...formDetails.register("ctc_max")} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Input label="Location" placeholder="Noida, India" {...formDetails.register("location")} />
                  <Input label="Application Deadline" type="date" {...formDetails.register("deadline")} />
                </div>
                <div className="pt-4 flex justify-end">
                  <Button type="submit">Continue to JD</Button>
                </div>
              </form>
            </motion.div>
          )}

          {/* STEP 2 */}
          {step === 2 && (
            <motion.div key="step2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
              <h3 className="text-lg font-medium">JOB DESCRIPTION</h3>
              <p className="text-sm text-muted-foreground">How would you like to add your JD?</p>
              
              <div className="grid grid-cols-2 gap-4">
                <div 
                  className={`p-6 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${uploadMethod === 'FILE' ? 'border-primary bg-primary/5' : 'border-border'}`}
                  onClick={() => setUploadMethod('FILE')}
                >
                  <UploadCloud className="mx-auto mb-2 text-muted-foreground" />
                  <span className="font-medium">Upload File</span>
                  <p className="text-xs text-muted-foreground mt-1">PDF, DOCX, TXT</p>
                </div>
                <div 
                  className={`p-6 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${uploadMethod === 'TEXT' ? 'border-primary bg-primary/5' : 'border-border'}`}
                  onClick={() => setUploadMethod('TEXT')}
                >
                  <FileText className="mx-auto mb-2 text-muted-foreground" />
                  <span className="font-medium">Paste / Write JD</span>
                  <p className="text-xs text-muted-foreground mt-1">Rich Text</p>
                </div>
              </div>

              {uploadMethod === 'FILE' ? (
                <div>
                  <input type="file" accept=".pdf,.docx,.txt" onChange={(e) => setJdFile(e.target.files?.[0] || null)} className="w-full text-sm mt-4 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-medium file:bg-primary/10 file:text-primary" />
                </div>
              ) : (
                <textarea 
                  className="w-full min-h-[200px] p-3 text-sm rounded-md border border-input bg-background" 
                  placeholder="Paste your JD text here..."
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                />
              )}

              <div className="pt-4 flex justify-end">
                <Button onClick={handleJdSubmit}>Extract Text</Button>
              </div>
            </motion.div>
          )}

          {/* STEP 3 */}
          {step === 3 && (
            <motion.div key="step3" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center justify-center min-h-[300px]">
              <Bot className="w-12 h-12 text-primary animate-pulse mb-6" />
              <h3 className="text-lg font-medium mb-4 uppercase tracking-widest text-muted-foreground">ANALYZING JOB DESCRIPTION</h3>
              <div className="space-y-3 w-64 text-sm font-medium">
                <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> Reading job requirements</div>
                <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-500" /> Identifying technical skills</div>
                <div className="flex items-center gap-2"><CircleDashed className="w-4 h-4 text-muted-foreground animate-spin" /> Preparing interview blueprint</div>
              </div>
            </motion.div>
          )}

          {/* STEP 4 */}
          {step === 4 && blueprint && analysis && (
            <motion.div key="step4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
              <h3 className="text-lg font-medium">AI INTERVIEW BLUEPRINT</h3>
              
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-muted p-4 rounded-md">
                  <p className="text-xs uppercase tracking-widest text-muted-foreground mb-2">AI Analysis</p>
                  <p className="text-sm"><strong>Role Level:</strong> {analysis.role_level}</p>
                  <p className="text-sm mt-1"><strong>Required Skills:</strong> {analysis.required_skills?.join(", ")}</p>
                  <p className="text-sm mt-1"><strong>Hard Req:</strong> {analysis.hard_requirements?.join(", ")}</p>
                </div>
                <div className="bg-muted p-4 rounded-md">
                  <p className="text-xs uppercase tracking-widest text-muted-foreground mb-2">Structure</p>
                  <p className="text-sm"><strong>Est. Duration:</strong> {blueprint.estimated_duration} mins</p>
                  <p className="text-sm mt-1"><strong>Intro Qs:</strong> {blueprint.question_distribution?.introduction}</p>
                  <p className="text-sm mt-1"><strong>Technical Qs:</strong> {blueprint.question_distribution?.technical}</p>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Evaluation Weights (%)</label>
                <div className="flex gap-4 mt-2">
                  <div className="flex-1"><Input type="number" label="Communication" value={blueprint.evaluation_weights.communication} onChange={(e) => setBlueprint({...blueprint, evaluation_weights: {...blueprint.evaluation_weights, communication: parseInt(e.target.value)}})} /></div>
                  <div className="flex-1"><Input type="number" label="Technical" value={blueprint.evaluation_weights.technical} onChange={(e) => setBlueprint({...blueprint, evaluation_weights: {...blueprint.evaluation_weights, technical: parseInt(e.target.value)}})} /></div>
                  <div className="flex-1"><Input type="number" label="Problem Solving" value={blueprint.evaluation_weights.problem_solving} onChange={(e) => setBlueprint({...blueprint, evaluation_weights: {...blueprint.evaluation_weights, problem_solving: parseInt(e.target.value)}})} /></div>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Minimum Resume Match Threshold (%)</label>
                <input type="range" min="40" max="95" value={blueprint.similarity_threshold} onChange={(e) => setBlueprint({...blueprint, similarity_threshold: parseInt(e.target.value)})} className="w-full mt-2 accent-primary" />
                <div className="text-center text-sm font-medium text-primary">{blueprint.similarity_threshold}%</div>
              </div>

              <div className="pt-4 flex justify-end">
                <Button onClick={handleBlueprintSave}>Approve & Continue</Button>
              </div>
            </motion.div>
          )}

          {/* STEP 5 */}
          {step === 5 && (
            <motion.div key="step5" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
              <h3 className="text-lg font-medium">REVIEW & PUBLISH</h3>
              
              <div className="border border-border rounded-md divide-y divide-border text-sm">
                <div className="p-4 flex justify-between"><span className="text-muted-foreground">Job Details</span><CheckCircle2 className="w-4 h-4 text-green-500"/></div>
                <div className="p-4 flex justify-between"><span className="text-muted-foreground">JD Uploaded</span><CheckCircle2 className="w-4 h-4 text-green-500"/></div>
                <div className="p-4 flex justify-between"><span className="text-muted-foreground">AI Analysis</span><CheckCircle2 className="w-4 h-4 text-green-500"/></div>
                <div className="p-4 flex justify-between"><span className="text-muted-foreground">Blueprint Configured</span><CheckCircle2 className="w-4 h-4 text-green-500"/></div>
                <div className="p-4 flex justify-between"><span className="text-muted-foreground">Resume Threshold</span><span className="font-medium">{blueprint?.similarity_threshold}%</span></div>
              </div>

              <div className="pt-4 flex justify-end gap-3">
                <Button variant="outline" onClick={() => router.push("/dashboard/company/jobs")}>Save as Draft</Button>
                <Button onClick={handlePublish}>Publish Job</Button>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  );
}
