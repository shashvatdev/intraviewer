
"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api/client";
import Link from "next/link";
import { Button } from "@/components/ui/button";

interface JobListItem {
  id: string;
  title: string;
  status: string;
  created_at: string;
}

export default function JobsListPage() {
  const [jobs, setJobs] = useState<JobListItem[]>([]);
  
  useEffect(() => {
    apiClient.get("/jobs").then(res => setJobs(res.data.data.jobs));
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-semibold">Your Jobs</h2>
          <p className="text-sm text-muted-foreground mt-1">Manage your job postings and interview blueprints.</p>
        </div>
        <Link href="/dashboard/company/jobs/create">
          <Button>Create New Job</Button>
        </Link>
      </div>
      
      <div className="space-y-4">
        {jobs.length === 0 ? (
          <div className="p-8 border border-border border-dashed rounded-lg text-center text-muted-foreground">
            No jobs created yet.
          </div>
        ) : (
          jobs.map(job => (
            <div key={job.id} className="p-4 border border-border bg-background rounded-lg flex items-center justify-between">
              <div>
                <h3 className="font-medium">{job.title}</h3>
                <span className="text-xs text-muted-foreground">{job.status} • {new Date(job.created_at).toLocaleDateString()}</span>
              </div>
              <Link href={`/dashboard/company/jobs/${job.id}`}>
                <Button variant="outline" size="sm">Manage</Button>
              </Link>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
