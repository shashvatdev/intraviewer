const fs = require('fs');
const path = 'src/app/(dashboard)/dashboard/company/profile/page.tsx';
let code = fs.readFileSync(path, 'utf8');

code = code.replace(
  /const { data } = await apiClient.get\("\/company\/profile"\);\n      setProfile\(data\);\n      setCompletion\(data.completion_percentage\);\n      reset\({/g,
  `const { data } = await apiClient.get("/company/profile");
      const profileData = data.data;
      setProfile(profileData);
      setCompletion(profileData.completion_percentage);
      reset({`
);

code = code.replace(
  /company_name: data.company_name \|\| "",\n        website: data.website \|\| "",\n        industry: data.industry \|\| "",\n        location: data.location \|\| "",\n        description: data.description \|\| "",/g,
  `company_name: profileData.company_name || "",
        website: profileData.website || "",
        industry: profileData.industry || "",
        location: profileData.location || "",
        description: profileData.description || "",`
);

code = code.replace(
  /const res = await apiClient.put\("\/company\/profile", data\);\n      setCompletion\(res.data.completion_percentage\);/g,
  `const res = await apiClient.put("/company/profile", data);
      setCompletion(res.data.data.completion_percentage);`
);

fs.writeFileSync(path, code);
