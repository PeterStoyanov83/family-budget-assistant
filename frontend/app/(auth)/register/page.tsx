"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const schema = z.object({
  email: z.string().email("Невалиден имейл"),
  password: z.string().min(8, "Минимум 8 знака"),
  first_name: z.string().optional(),
  household_size: z.coerce.number().int().min(1).max(12).default(2),
  city: z.string().optional(),
  has_car: z.boolean().default(true),
});
type FormData = z.infer<typeof schema>;

export default function RegisterPage() {
  const router = useRouter();
  const { setUser } = useAuth();
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  async function onSubmit(data: FormData) {
    try {
      const user = await authApi.register(data);
      setUser(user);
      router.push("/dashboard");
    } catch (err: any) {
      setError("root", { message: err.message });
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm bg-white rounded-[12px] shadow-sm border border-gray-100 p-8">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-primary-500">Family Budget</h1>
          <p className="text-sm text-gray-500 mt-1">Създайте профил безплатно</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Имейл *</label>
            <Input type="email" placeholder="ivan@example.com" {...register("email")} />
            {errors.email && <p className="text-xs text-red-500 mt-1">{errors.email.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Парола *</label>
            <Input type="password" placeholder="Минимум 8 знака" {...register("password")} />
            {errors.password && <p className="text-xs text-red-500 mt-1">{errors.password.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Как да се обръщаме?</label>
            <Input placeholder="Иван" {...register("first_name")} />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Членове</label>
              <Input type="number" min={1} max={12} defaultValue={2} {...register("household_size")} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Град</label>
              <Input placeholder="София" {...register("city")} />
            </div>
          </div>

          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" defaultChecked {...register("has_car")}
              className="w-4 h-4 accent-primary-500" />
            <span className="text-sm text-gray-700">Имам кола</span>
          </label>

          {errors.root && (
            <p className="text-sm text-red-500 text-center">{errors.root.message}</p>
          )}

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? "Регистрация..." : "Регистрация"}
          </Button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Вече имате профил?{" "}
          <Link href="/login" className="text-primary-500 font-medium hover:underline">
            Вход
          </Link>
        </p>
      </div>
    </div>
  );
}
