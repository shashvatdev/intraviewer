import os

with open("src/app/(dashboard)/dashboard/company/jobs/[id]/page.tsx", "r") as f:
    content = f.read()

old_ui = """                     <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                           <p className="text-xs text-blue-600 uppercase font-semibold">Technical Score</p>
                           <p className="text-2xl font-bold text-blue-900 mt-1">{app.session.evaluation_score}/100</p>
                        </div>
                        <div className={`p-4 rounded-lg border ${app.session.integrity_score < 70 ? 'bg-red-50 border-red-100' : 'bg-green-50 border-green-100'}`}>
                           <p className={`text-xs uppercase font-semibold ${app.session.integrity_score < 70 ? 'text-red-600' : 'text-green-600'}`}>Integrity Score</p>
                           <p className={`text-2xl font-bold mt-1 ${app.session.integrity_score < 70 ? 'text-red-900' : 'text-green-900'}`}>{app.session.integrity_score}%</p>
                        </div>
                     </div>"""

new_ui = """                     <div className="grid grid-cols-2 gap-4 mb-4">
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
                     
                     {app.session.evaluation_details?.logistics_responses && (
                        <div className="mb-6 bg-gray-50 border border-gray-100 p-4 rounded-lg">
                           <p className="text-sm font-semibold text-gray-700 mb-1">Logistics / Availability</p>
                           <p className="text-sm text-gray-600">{app.session.evaluation_details.logistics_responses}</p>
                        </div>
                     )}"""

content = content.replace(old_ui, new_ui)

with open("src/app/(dashboard)/dashboard/company/jobs/[id]/page.tsx", "w") as f:
    f.write(content)

print("Updated Company UI with detailed analysis")
