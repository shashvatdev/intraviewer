import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

candidate_jobs_page = """
"use client";

import { useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api/client";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, MapPin, Briefcase, Clock, ChevronLeft, ChevronRight } from "lucide-react";

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
            <Button>Apply Now</Button>
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
    <div className="space-y-10">
      
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

    </div>
  );
}
"""

write_file("src/app/(dashboard)/dashboard/candidate/jobs/page.tsx", candidate_jobs_page)

