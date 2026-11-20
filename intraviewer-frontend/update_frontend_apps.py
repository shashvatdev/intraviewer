import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

# Update Candidate Jobs Page to include Apply Modal
candidate_jobs_page = """
"use client";

import { useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api/client";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, MapPin, Briefcase, Clock, ChevronLeft, ChevronRight, X, UploadCloud, CheckCircle2, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { AnimatePresence, motion } from "framer-motion";

export default function CandidateJobsPage() {
  const [jobs, setJobs] = useState([]);
  const [recommended, setRecommended] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const limit = 10;
  
  // Filters
  const [q, setQ] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [location, setLocation] = useState("");
  const [workMode, setWorkMode] = useState("");
  const [expMin, setExpMin] = useState("");
  
  // Apply Modal state
  const [applyJob, setApplyJob] = useState<any>(null);
  const [resumeFile, setResumeFile] = useState<File|null>(null);
  const [isApplying, setIsApplying] = useState(false);
  const [applyResult, setApplyResult] = useState<any>(null);

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append("page", page.toString());
      params.append("limit", limit.toString());
      if (searchQuery) params.append("q", searchQuery);
      if (location) params.append("location", location);
      if (workMode) params.append("work_mode", workMode);
      if (expMin) params.append("experience_min", expMin);
      
      const res = await apiClient.get(`/candidate/jobs/search?${params.toString()}`);
      setJobs(res.data.data.jobs);
      setTotal(res.data.data.total);
      setTotalPages(res.data.data.total_pages);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [page, limit, searchQuery, location, workMode, expMin]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  useEffect(() => {
    apiClient.get("/candidate/jobs/recommended?limit=3").then(res => {
      setRecommended(res.data.data.jobs);
    });
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setSearchQuery(q);
  };
  
  const submitApplication = async () => {
    if (!resumeFile || !applyJob) return;
    setIsApplying(true);
    try {
      const formData = new FormData();
      formData.append("file", resumeFile);
      const res = await apiClient.post(`/applications/candidate/jobs/${applyJob.id}/apply`, formData);
      setApplyResult(res.data.data);
      // Update local state to show 'Applied'
      setJobs(jobs.map((j: any) => j.id === applyJob.id ? {...j, has_applied: true} : j) as any);
      setRecommended(recommended.map((j: any) => j.id === applyJob.id ? {...j, has_applied: true} : j) as any);
    } catch (e: any) {
      toast.error(e.response?.data?.message || "Failed to apply");
      setApplyJob(null);
    } finally {
      setIsApplying(false);
    }
  };

  const closeApplyModal = () => {
    setApplyJob(null);
    setResumeFile(null);
    setApplyResult(null);
  };

  const JobCard = ({ job, isRecommended=false }: { job: any, isRecommended?: boolean }) => {
    return (
      <div className={`p-5 rounded-lg border ${isRecommended ? 'border-primary/50 bg-primary/5' : 'border-border bg-background'} flex flex-col gap-4`}>
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold text-foreground">{job.title}</h3>
            <p className="text-sm font-medium text-muted-foreground">{job.company_name}</p>
          </div>
          {job.has_applied ? (
            <Button variant="secondary" disabled>Applied</Button>
          ) : (
            <Button onClick={() => setApplyJob(job)}>Apply Now</Button>
          )}
        </div>
        
        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
          {job.location && <div className="flex items-center gap-1"><MapPin className="w-4 h-4"/> {job.location}</div>}
          {(job.experience_min !== null) && <div className="flex items-center gap-1"><Briefcase className="w-4 h-4"/> {job.experience_min}-{job.experience_max} Years</div>}
          {job.work_mode && <div className="flex items-center gap-1"><Clock className="w-4 h-4"/> {job.work_mode}</div>}
          {(job.ctc_min || job.ctc_max) && <div className="font-medium text-foreground">₹{job.ctc_min}-{job.ctc_max} LPA</div>}
        </div>
        
        {job.required_skills && job.required_skills.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {job.required_skills.map((s: string, i: number) => (
              <span key={i} className="px-2 py-1 bg-muted rounded text-xs font-medium">{s}</span>
            ))}
          </div>
        )}
        
        <div className="text-xs text-muted-foreground mt-2 border-t border-border/50 pt-3 flex justify-between">
          <span>Posted: {new Date(job.created_at).toLocaleDateString()}</span>
          {job.deadline && <span>Closes: {new Date(job.deadline).toLocaleDateString()}</span>}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-10 relative">
      
      {/* Search Header */}
      <div className="bg-background border border-border p-6 rounded-lg space-y-4">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="w-5 h-5 absolute left-3 top-3 text-muted-foreground" />
            <input 
              type="text"
              placeholder="Search jobs by title, skill or company..."
              className="w-full pl-10 pr-4 py-2 rounded-md border border-input bg-background text-sm focus:ring-1 focus:ring-primary outline-none"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>
          <Button type="submit">Search</Button>
        </form>
        
        <div className="flex flex-wrap gap-4 items-center border-t border-border pt-4">
          <span className="text-sm font-medium text-muted-foreground">Filters:</span>
          <select className="text-sm border border-input rounded p-1 bg-background" value={location} onChange={e => {setLocation(e.target.value); setPage(1)}}>
            <option value="">All Locations</option>
            <option value="Noida">Noida</option>
            <option value="Bangalore">Bangalore</option>
            <option value="Remote">Remote</option>
          </select>
          <select className="text-sm border border-input rounded p-1 bg-background" value={workMode} onChange={e => {setWorkMode(e.target.value); setPage(1)}}>
            <option value="">Any Work Mode</option>
            <option value="Remote">Remote</option>
            <option value="Hybrid">Hybrid</option>
            <option value="On-site">On-site</option>
          </select>
          <select className="text-sm border border-input rounded p-1 bg-background" value={expMin} onChange={e => {setExpMin(e.target.value); setPage(1)}}>
            <option value="">Any Experience</option>
            <option value="0">Fresher (0 years)</option>
            <option value="1">1+ Years</option>
            <option value="3">3+ Years</option>
            <option value="5">5+ Years</option>
          </select>
        </div>
      </div>

      {/* Recommended Section */}
      {recommended.length > 0 && page === 1 && !searchQuery && !location && !workMode && !expMin && (
        <div>
          <h2 className="text-xl font-bold tracking-tight mb-4 flex items-center gap-2">
             <span className="text-primary">✦</span> Recommended for You
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommended.map((job: any) => (
              <JobCard key={job.id} job={job} isRecommended={true} />
            ))}
          </div>
        </div>
      )}

      {/* All Active Jobs */}
      <div>
        <h2 className="text-xl font-bold tracking-tight mb-4">
          All Active Jobs <span className="text-muted-foreground font-normal text-base">({total})</span>
        </h2>
        
        {loading ? (
          <div className="py-12 text-center text-muted-foreground">Loading jobs...</div>
        ) : jobs.length === 0 ? (
          <div className="py-12 text-center border border-border border-dashed rounded-lg text-muted-foreground">
            No active jobs found matching your criteria.
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job: any) => (
              <JobCard key={job.id} job={job} />
            ))}
            
            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-4 mt-8 pt-4">
                <Button variant="outline" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
                  <ChevronLeft className="w-4 h-4 mr-1"/> Prev
                </Button>
                <span className="text-sm font-medium">Page {page} of {totalPages}</span>
                <Button variant="outline" size="sm" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
                  Next <ChevronRight className="w-4 h-4 ml-1"/>
                </Button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Apply Modal */}
      <AnimatePresence>
        {applyJob && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 backdrop-blur-sm"
          >
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              className="bg-background border border-border rounded-xl shadow-lg w-full max-w-md overflow-hidden relative"
            >
              <button onClick={closeApplyModal} className="absolute right-4 top-4 text-muted-foreground hover:text-foreground"><X className="w-5 h-5"/></button>
              
              <div className="p-6">
                <h2 className="text-xl font-bold mb-1">Apply for {applyJob.title}</h2>
                <p className="text-sm text-muted-foreground mb-6">{applyJob.company_name}</p>
                
                {!applyResult ? (
                  isApplying ? (
                    <div className="flex flex-col items-center justify-center py-8">
                      <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mb-4" />
                      <p className="font-medium text-center">AI is analyzing your resume...</p>
                      <p className="text-sm text-muted-foreground mt-2 text-center">Comparing your skills against the Job Description.</p>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      <div className="p-4 border-2 border-dashed border-border rounded-lg text-center hover:bg-muted/50 transition-colors">
                        <UploadCloud className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
                        <p className="text-sm font-medium">Upload your Resume</p>
                        <p className="text-xs text-muted-foreground mt-1">PDF, DOCX, TXT</p>
                        <input type="file" accept=".pdf,.docx,.txt" onChange={e => setResumeFile(e.target.files?.[0] || null)} className="mt-4 w-full text-sm" />
                      </div>
                      <Button className="w-full" onClick={submitApplication} disabled={!resumeFile}>Submit Application</Button>
                    </div>
                  )
                ) : (
                  <div className="space-y-6 text-center">
                    {applyResult.status === "SHORTLISTED" ? (
                      <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto" />
                    ) : (
                      <AlertCircle className="w-16 h-16 text-red-500 mx-auto" />
                    )}
                    <div>
                      <h3 className="text-lg font-bold">{applyResult.status === "SHORTLISTED" ? "Application Accepted!" : "Application Rejected"}</h3>
                      <p className="text-sm text-muted-foreground mt-2">
                        {applyResult.status === "SHORTLISTED" 
                          ? "Your resume meets the requirements. You will be invited to an AI interview shortly."
                          : "Unfortunately, your resume did not meet the minimum match threshold for this role."}
                      </p>
                    </div>
                    <div className="bg-muted p-4 rounded-lg flex items-center justify-between">
                      <span className="text-sm font-medium">AI Match Score</span>
                      <span className={`text-xl font-bold ${applyResult.score >= applyResult.threshold ? 'text-green-600' : 'text-red-600'}`}>{applyResult.score}%</span>
                    </div>
                    <div className="text-sm bg-background border border-border p-3 rounded-lg text-left">
                      <strong>AI Reasoning:</strong> {applyResult.reasoning}
                    </div>
                    <Button className="w-full" onClick={closeApplyModal}>Close</Button>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
"""

write_file("src/app/(dashboard)/dashboard/candidate/jobs/page.tsx", candidate_jobs_page)

candidate_my_apps = """
"use client";
import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api/client";

export default function MyApplicationsPage() {
  const [apps, setApps] = useState([]);
  useEffect(() => {
    apiClient.get("/applications/candidate/applications").then(res => setApps(res.data.data.applications));
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6">My Applications</h2>
      <div className="space-y-4">
        {apps.length === 0 ? (
          <div className="text-muted-foreground">No applications yet.</div>
        ) : (
          apps.map((app: any) => (
            <div key={app.id} className="p-4 bg-background border border-border rounded-lg flex justify-between items-center">
              <div>
                <h3 className="font-medium text-lg">{app.job_title}</h3>
                <p className="text-sm text-muted-foreground">Applied: {new Date(app.created_at).toLocaleDateString()}</p>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-xs text-muted-foreground uppercase">Match Score</p>
                  <p className="font-bold">{app.match_score}%</p>
                </div>
                <div className={`px-3 py-1 text-xs font-medium rounded-full ${app.status === 'SHORTLISTED' ? 'bg-green-100 text-green-700' : app.status === 'REJECTED' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>
                  {app.status}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
"""
write_file("src/app/(dashboard)/dashboard/candidate/applications/page.tsx", candidate_my_apps)

company_job_manage = """
"use client";
import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api/client";
import { useParams } from "next/navigation";
import { FileText, CheckCircle } from "lucide-react";

export default function CompanyManageJobPage() {
  const params = useParams();
  const [job, setJob] = useState<any>(null);
  const [apps, setApps] = useState([]);

  useEffect(() => {
    apiClient.get(`/jobs/${params.id}`).then(res => setJob(res.data.data));
    apiClient.get(`/applications/company/jobs/${params.id}/applications`).then(res => setApps(res.data.data.applications));
  }, [params.id]);

  if (!job) return <div>Loading...</div>;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-semibold">{job.title}</h2>
        <div className="flex gap-4 mt-2 text-sm text-muted-foreground">
          <span>{job.department}</span> • <span>{job.location}</span> • <span>Status: {job.status}</span>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4 border-b border-border pb-2">Applications ({apps.length})</h3>
        <div className="space-y-4">
          {apps.map((app: any) => (
            <div key={app.id} className="p-4 bg-background border border-border rounded-lg">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h4 className="font-medium">{app.candidate_name}</h4>
                  <p className="text-sm text-muted-foreground">{app.candidate_email}</p>
                </div>
                <div className="flex gap-3">
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground uppercase mb-1">Match</p>
                    <span className="font-bold text-lg text-primary">{app.match_score}%</span>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground uppercase mb-1">Status</p>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${app.status === 'SHORTLISTED' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {app.status}
                    </span>
                  </div>
                </div>
              </div>
              <div className="bg-muted p-3 rounded text-sm text-muted-foreground">
                <strong className="text-foreground">AI Reasoning:</strong> {app.reasoning}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
"""
write_file("src/app/(dashboard)/dashboard/company/jobs/[id]/page.tsx", company_job_manage)

