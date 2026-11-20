"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { apiClient } from "@/lib/api/client";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

type ProfileData = {
  name: string;
  phone: string;
  github_url: string;
  linkedin_url: string;
  portfolio_url: string;
  skills: string; // for simplicity, comma separated in form
};

export default function CandidateProfilePage() {
  const [completion, setCompletion] = useState(0);
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm<ProfileData>();

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const { data } = await apiClient.get("/candidate/profile");
      const profileData = data.data;
      setCompletion(profileData.completion_percentage);
      reset({
        name: profileData.name || "",
        phone: profileData.phone || "",
        github_url: profileData.github_url || "",
        linkedin_url: profileData.linkedin_url || "",
        portfolio_url: profileData.portfolio_url || "",
        skills: Array.isArray(profileData.skills) ? profileData.skills.join(", ") : "",
      });
    } catch (error) {
      toast.error("Failed to load profile");
    }
  };

  const onSubmit = async (data: ProfileData) => {
    try {
      const payload = {
        ...data,
        skills: data.skills.split(",").map(s => s.trim()).filter(Boolean),
      };
      const res = await apiClient.put("/candidate/profile", payload);
      setCompletion(res.data.data.completion_percentage);
      toast.success("Profile updated successfully");
    } catch (error) {
      toast.error("Failed to update profile");
    }
  };

  return (
    <div className="bg-background border border-border rounded-lg p-6 sm:p-8 shadow-sm">
      <div className="mb-8">
        <h2 className="text-2xl font-bold">Candidate Profile</h2>
        <p className="text-muted-foreground text-sm mt-1">Manage your public profile information.</p>
        
        <div className="mt-4 bg-muted rounded-full overflow-hidden h-2.5 w-full max-w-md">
          <div 
            className="bg-primary h-full transition-all duration-500 ease-in-out" 
            style={{ width: `${completion}%` }}
          />
        </div>
        <p className="text-xs font-medium mt-2 text-muted-foreground uppercase tracking-wider">
          PROFILE COMPLETION {completion}%
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-2xl">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input label="Full Name" {...register("name")} />
          <Input label="Phone Number" {...register("phone")} />
        </div>
        
        <div>
          <Input label="Skills (comma separated)" placeholder="React, Python, Machine Learning" {...register("skills")} />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input label="GitHub URL" type="url" placeholder="https://github.com/..." {...register("github_url")} />
          <Input label="LinkedIn URL" type="url" placeholder="https://linkedin.com/in/..." {...register("linkedin_url")} />
        </div>

        <div>
          <Input label="Portfolio URL" type="url" placeholder="https://yourwebsite.com" {...register("portfolio_url")} />
        </div>

        <div className="pt-4 flex justify-end">
          <Button type="submit" isLoading={isSubmitting}>
            Save Changes
          </Button>
        </div>
      </form>
    </div>
  );
}
