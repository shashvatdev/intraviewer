const fs = require('fs');
const path = 'src/app/(dashboard)/dashboard/candidate/profile/page.tsx';
let code = fs.readFileSync(path, 'utf8');

code = code.replace(
  /const { data } = await apiClient.get\("\/candidate\/profile"\);\n      setCompletion\(data.completion_percentage\);\n      reset\({/g,
  `const { data } = await apiClient.get("/candidate/profile");
      const profileData = data.data;
      setCompletion(profileData.completion_percentage);
      reset({`
);

code = code.replace(
  /name: data.name \|\| "",\n        phone: data.phone \|\| "",\n        github_url: data.github_url \|\| "",\n        linkedin_url: data.linkedin_url \|\| "",\n        portfolio_url: data.portfolio_url \|\| "",\n        skills: Array.isArray\(data.skills\) \? data.skills.join\(", "\) : "",/g,
  `name: profileData.name || "",
        phone: profileData.phone || "",
        github_url: profileData.github_url || "",
        linkedin_url: profileData.linkedin_url || "",
        portfolio_url: profileData.portfolio_url || "",
        skills: Array.isArray(profileData.skills) ? profileData.skills.join(", ") : "",`
);

code = code.replace(
  /const res = await apiClient.put\("\/candidate\/profile", payload\);\n      setCompletion\(res.data.completion_percentage\);/g,
  `const res = await apiClient.put("/candidate/profile", payload);
      setCompletion(res.data.data.completion_percentage);`
);

fs.writeFileSync(path, code);
