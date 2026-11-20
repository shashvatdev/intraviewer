"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { apiClient } from "@/lib/api/client";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

type CompanyProfileData = {
  company_name: string;
  website: string;
  industry: string;
  location: string;
  description: string;
};

export default function CompanyProfilePage() {
  const [completion, setCompletion] = useState(0);
  const [profile, setProfile] = useState<any>(null);
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm<CompanyProfileData>();

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const { data } = await apiClient.get("/company/profile");
      const profileData = data.data;
      setProfile(profileData);
      setCompletion(profileData.completion_percentage);
      reset({
        company_name: profileData.company_name || "",
        website: profileData.website || "",
        industry: profileData.industry || "",
        location: profileData.location || "",
        description: profileData.description || "",
      });
    } catch (error) {
      toast.error("Failed to load company profile");
    }
  };

  const onSubmit = async (data: CompanyProfileData) => {
    try {
      const res = await apiClient.put("/company/profile", data);
      setCompletion(res.data.data.completion_percentage);
      toast.success("Company profile updated successfully");
      fetchProfile(); // refresh preview
    } catch (error) {
      toast.error("Failed to update profile");
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-2 bg-background border border-border rounded-lg p-6 sm:p-8 shadow-sm h-fit">
        <div className="mb-8">
          <h2 className="text-2xl font-bold">Company Profile</h2>
          <p className="text-muted-foreground text-sm mt-1">Manage your company's public information.</p>
          
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

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="Company Name" {...register("company_name")} />
            <Input label="Industry" placeholder="Software & AI" {...register("industry")} />
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="Website" type="url" placeholder="https://company.com" {...register("website")} />
            <Input label="Location" placeholder="San Francisco, CA" {...register("location")} />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">Company Description</label>
            <textarea
              {...register("description")}
              rows={4}
              className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              placeholder="Building intelligent products for modern businesses."
            />
          </div>

          <div className="pt-4 flex justify-end">
            <Button type="submit" isLoading={isSubmitting}>
              Save Changes
            </Button>
          </div>
        </form>
      </div>

      {/* Preview Card */}
      <div className="bg-background border border-border rounded-lg p-6 shadow-sm h-fit sticky top-6">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">Preview</h3>
        <div className="border border-border rounded-md p-5 bg-white/50">
          <div className="w-12 h-12 bg-muted rounded-md flex items-center justify-center text-xl font-bold text-muted-foreground mb-4">
            {profile?.company_name?.[0]?.toUpperCase() || "C"}
          </div>
          <h4 className="text-lg font-bold text-foreground">{profile?.company_name || "Company Name"}</h4>
          <p className="text-sm text-primary font-medium mt-1">{profile?.industry || "Industry"}</p>
          
          <p className="text-sm text-muted-foreground mt-4 line-clamp-4">
            {profile?.description || "No description provided yet."}
          </p>

          <div className="mt-6 space-y-2">
            {profile?.website && (
              <div className="flex items-center gap-2 text-sm text-foreground">
                <span className="text-muted-foreground">🌐</span> {profile.website}
              </div>
            )}
            {profile?.location && (
              <div className="flex items-center gap-2 text-sm text-foreground">
                <span className="text-muted-foreground">📍</span> {profile.location}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
