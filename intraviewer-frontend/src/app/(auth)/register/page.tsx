import Link from "next/link";
import { ArrowRight, Building2, User } from "lucide-react";

const CHOICES = [
  {
    href: "/register/candidate",
    icon: User,
    title: "I'm a Candidate",
    description: "Practice mock interviews, apply to roles and get AI-vetted.",
    accent: "from-indigo-500/20 to-violet-500/10 text-indigo-300",
  },
  {
    href: "/register/company",
    icon: Building2,
    title: "I'm Hiring",
    description: "Post roles and let AI run first-round technical & behavioral screens.",
    accent: "from-cyan-500/20 to-emerald-500/10 text-cyan-300",
  },
];

export default function RegisterPage() {
  return (
    <div className="w-full">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold tracking-tight">Create your account</h2>
        <p className="mt-1.5 text-sm text-muted-foreground">Choose how you&apos;ll use IntraViewer.</p>
      </div>

      <div className="space-y-3">
        {CHOICES.map(({ href, icon: Icon, title, description, accent }) => (
          <Link
            key={href}
            href={href}
            className="group flex items-center gap-4 rounded-xl border border-white/10 bg-white/[0.02] p-4 transition-all hover:-translate-y-0.5 hover:border-indigo-400/40 hover:bg-white/[0.04]"
          >
            <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br ${accent}`}>
              <Icon className="h-5 w-5" />
            </span>
            <span className="flex-1">
              <span className="block text-sm font-medium text-white">{title}</span>
              <span className="mt-0.5 block text-xs leading-relaxed text-muted-foreground">{description}</span>
            </span>
            <ArrowRight className="h-4 w-4 text-zinc-500 transition-all group-hover:translate-x-0.5 group-hover:text-white" />
          </Link>
        ))}
      </div>

      <div className="mt-6 border-t border-white/[0.06] pt-5 text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-white underline-offset-4 hover:underline">
          Sign in
        </Link>
      </div>
    </div>
  );
}
