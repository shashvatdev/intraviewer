
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiClient } from "@/lib/api/client";
import { FileText, Star, Clock, CheckCircle, XCircle, ChevronDown, ShieldAlert, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function CompanyJobView() {
  const params = useParams();
  const [job, setJob] = useState<any>(null);
  const [apps, setApps] = useState([]);
  const [expandedApp, setExpandedApp] = useState<string | null>(null);

  useEffect(() => {
    apiClient.get(`/jobs/${params.id}`).then(res => setJob(res.data.data));
    apiClient.get(`/company/jobs/${params.id}/applications`).then(res => setApps(res.data.data.applications));
  }, [params.id]);

  if (!job) return <div>Loading...</div>;

  return (
    <div className="max-w-5xl mx-auto py-8">
      <div className="mb-8 border-b pb-6">
        <h1 className="text-3xl font-bold">{job.title}</h1>
        <p className="text-muted-foreground mt-2">{job.department} • {job.location} • {job.work_mode}</p>
      </div>

      <h2 className="text-xl font-semibold mb-6">Applicants ({apps.length})</h2>
      
      <div className="space-y-4">
        {apps.length === 0 && <p className="text-muted-foreground">No applications yet.</p>}
        {apps.map((app: any) => (
          <div key={app.id} className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
            <div className="p-6 flex flex-col md:flex-row justify-between items-center cursor-pointer hover:bg-gray-50" onClick={() => setExpandedApp(expandedApp === app.id ? null : app.id)}>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center font-bold text-lg">
                  {app.candidate_name.charAt(0)}
                </div>
                <div>
                  <h3 className="font-semibold text-lg">{app.candidate_name}</h3>
                  <p className="text-sm text-gray-500">{app.candidate_email}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-8 mt-4 md:mt-0">
                <div className="text-center">
                  <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Resume Match</p>
                  <div className={`font-bold text-lg ${app.match_score >= 70 ? 'text-green-600' : 'text-orange-600'}`}>
                    {app.match_score}%
                  </div>
                </div>
                
                {app.session?.status === "COMPLETED" && (
                  <div className="text-center">
                    <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">AI Tech Score</p>
                    <div className="font-bold text-lg text-blue-600">
                      {app.session.evaluation_score || "N/A"}/100
                    </div>
                  </div>
                )}
                
                <div className="w-32 flex justify-end">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${app.status === 'EVALUATING' ? 'bg-blue-100 text-blue-800' : app.status === 'SHORTLISTED' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {app.status}
                  </span>
                </div>
                <ChevronDown className={`w-5 h-5 text-gray-400 transform transition-transform ${expandedApp === app.id ? 'rotate-180' : ''}`} />
              </div>
            </div>
            
            {expandedApp === app.id && (
              <div className="border-t border-gray-100 bg-gray-50 p-6 space-y-6">
                
                {/* Stage 1: Resume Analysis */}
                <div className="bg-white p-5 rounded-lg border border-gray-100 shadow-sm">
                   <h4 className="font-semibold text-gray-800 mb-2 flex items-center gap-2"><FileText className="w-4 h-4"/> AI Resume Analysis</h4>
                   <p className="text-sm text-gray-600">{app.reasoning}</p>
                   <div className="mt-4">
                     <a href={`#`} className="text-sm text-[#6B52FF] hover:underline flex items-center gap-1">
                        Download Original Resume: {app.resume_filename}
                     </a>
                   </div>
                </div>

                {/* Stage 2: AI Interview Report */}
                {app.session && app.session.status === "COMPLETED" && (
                  <div className="bg-white p-5 rounded-lg border border-gray-100 shadow-sm">
                     <h4 className="font-semibold text-gray-800 mb-4 flex items-center gap-2"><Star className="w-4 h-4 text-[#6B52FF]"/> Live AI Interview Report</h4>
                     
                     <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="p-4 bg-blue-50 rounded-lg border border-blue-100 flex flex-col justify-center">
                           <p className="text-xs text-blue-600 uppercase font-semibold">AI Technical Score</p>
                           <p className="text-3xl font-bold text-blue-900 mt-1">{app.session.evaluation_score || 0}/100</p>
                        </div>
                        <div className={`p-4 rounded-lg border flex flex-col justify-center ${app.session.integrity_score < 70 ? 'bg-red-50 border-red-100' : 'bg-green-50 border-green-100'}`}>
                           <p className={`text-xs uppercase font-semibold ${app.session.integrity_score < 70 ? 'text-red-600' : 'text-green-600'}`}>Integrity Score</p>
                           <p className={`text-3xl font-bold mt-1 ${app.session.integrity_score < 70 ? 'text-red-900' : 'text-green-900'}`}>{app.session.integrity_score}%</p>
                        </div>
                     </div>
                     
                     {app.session.evaluation_details?.detailed_analysis && (
                        <div className="mb-6 bg-[#6B52FF]/5 border border-[#6B52FF]/20 p-4 rounded-lg">
                           <p className="text-sm font-semibold text-[#6B52FF] mb-2">Detailed AI Assessment</p>
                           <p className="text-sm text-gray-700 leading-relaxed">{app.session.evaluation_details.detailed_analysis}</p>
                        </div>
                     )}
                     
                     {app.session.evaluation_details?.logistics_responses && typeof app.session.evaluation_details.logistics_responses === 'string' && (
                        <div className="mb-6 bg-gray-50 border border-gray-100 p-4 rounded-lg">
                           <p className="text-sm font-semibold text-gray-700 mb-1">Logistics / Availability</p>
                           <p className="text-sm text-gray-600">{app.session.evaluation_details.logistics_responses}</p>
                        </div>
                     )}
                     {app.session.evaluation_details?.logistics_responses && typeof app.session.evaluation_details.logistics_responses === 'object' && Object.keys(app.session.evaluation_details.logistics_responses).length > 0 && (
                        <div className="mb-6 bg-gray-50 border border-gray-100 p-4 rounded-lg">
                           <p className="text-sm font-semibold text-gray-700 mb-1">Logistics / Availability</p>
                           <p className="text-sm text-gray-600">{JSON.stringify(app.session.evaluation_details.logistics_responses)}</p>
                        </div>
                     )}

                     {/* Proctoring Logs */}
                     {app.session.proctoring_logs && app.session.proctoring_logs.length > 0 && (
                        <div className="mb-6">
                           <p className="text-sm font-semibold text-red-600 flex items-center gap-2 mb-2"><ShieldAlert className="w-4 h-4"/> Proctoring Violations</p>
                           <div className="bg-red-50 rounded border border-red-100 p-3 space-y-2">
                             {app.session.proctoring_logs.map((log: any, i: number) => (
                               <div key={i} className="text-xs text-red-800 flex items-start gap-2">
                                  <AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                                  <span>{log.description}</span>
                               </div>
                             ))}
                           </div>
                        </div>
                     )}

                     {/* Transcript */}
                     <div>
                        <p className="text-sm font-semibold text-gray-800 mb-2">Interview Transcript</p>
                        <div className="h-64 overflow-y-auto bg-gray-50 rounded border p-4 space-y-3">
                           {app.session.transcript.map((msg: any, i: number) => (
                              <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                                 <span className="text-[10px] text-gray-400 font-medium mb-1 uppercase">{msg.role === 'user' ? 'Candidate' : 'AI Recruiter'}</span>
                                 <div className={`px-3 py-2 text-sm rounded-lg max-w-[85%] ${msg.role === 'user' ? 'bg-[#6B52FF] text-white' : 'bg-gray-200 text-gray-800'}`}>
                                    {msg.content}
                                 </div>
                              </div>
                           ))}
                        </div>
                     </div>
                  </div>
                )}
                
                {app.session?.status === "COMPLETED" ? (
                  <div className="flex gap-4 pt-2">
                    <Button className="w-full bg-green-600 hover:bg-green-700 text-white gap-2"><CheckCircle className="w-4 h-4"/> Hire Candidate</Button>
                    <Button variant="outline" className="w-full text-red-600 border-red-200 hover:bg-red-50 gap-2"><XCircle className="w-4 h-4"/> Reject</Button>
                  </div>
                ) : (
                  <div className="flex justify-center p-4">
                     <p className="text-sm text-gray-500 italic">Waiting for candidate to complete the AI interview...</p>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
