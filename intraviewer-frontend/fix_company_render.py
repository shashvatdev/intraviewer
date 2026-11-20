with open("src/app/(dashboard)/dashboard/company/jobs/[id]/page.tsx", "r") as f:
    content = f.read()

old_block = """                     {app.session.evaluation_details?.logistics_responses && (
                        <div className="mb-6 bg-gray-50 border border-gray-100 p-4 rounded-lg">
                           <p className="text-sm font-semibold text-gray-700 mb-1">Logistics / Availability</p>
                           <p className="text-sm text-gray-600">{app.session.evaluation_details.logistics_responses}</p>
                        </div>
                     )}"""

new_block = """                     {app.session.evaluation_details?.logistics_responses && typeof app.session.evaluation_details.logistics_responses === 'string' && (
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
                     )}"""

content = content.replace(old_block, new_block)

with open("src/app/(dashboard)/dashboard/company/jobs/[id]/page.tsx", "w") as f:
    f.write(content)

print("Fixed render bug!")
