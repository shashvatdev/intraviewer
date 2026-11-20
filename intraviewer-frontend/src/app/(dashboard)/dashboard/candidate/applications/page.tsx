
"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api/client";
import { Button } from "@/components/ui/button";
import { Video } from "lucide-react";

export default function MyApplicationsPage() {
  const [apps, setApps] = useState([]);
  const router = useRouter();
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    apiClient.get("/candidate/applications").then(res => setApps(res.data.data.applications));
  }, []);

  const handleStartInterview = async (appId: string) => {
    setStarting(true);
    try {
      const res = await apiClient.post(`/applications/${appId}/start-interview`);
      const sessionId = res.data.data.session_id;
      router.push(`/interview/${sessionId}`);
    } catch(e) {
      console.error(e);
      setStarting(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6">My Applications</h2>
      <div className="space-y-4">
        {apps.length === 0 ? (
          <div className="text-muted-foreground">No applications yet.</div>
        ) : (
          apps.map((app: any) => (
            <div key={app.id} className="p-4 bg-background border border-border rounded-lg flex flex-col md:flex-row md:justify-between md:items-center gap-4">
              <div>
                <h3 className="font-medium text-lg">{app.job_title}</h3>
                <p className="text-sm text-muted-foreground">Applied: {new Date(app.created_at).toLocaleDateString()}</p>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-center">
                  <p className="text-xs text-muted-foreground uppercase">Match Score</p>
                  <p className="font-bold">{app.match_score}%</p>
                </div>
                <div className={`px-3 py-1 text-xs font-medium rounded-full flex items-center justify-center min-w-[100px] ${app.status === 'SHORTLISTED' ? 'bg-green-100 text-green-700' : app.status === 'REJECTED' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>
                  {app.status}
                </div>
                {app.status === 'SHORTLISTED' && (
                  <Button onClick={() => handleStartInterview(app.id)} disabled={starting} className="gap-2 bg-[#6B52FF] hover:bg-[#5b45df]">
                    <Video className="w-4 h-4" /> Join Interview
                  </Button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
