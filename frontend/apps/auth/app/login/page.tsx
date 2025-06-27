'use client'

import { cn } from "@/lib/utils"
import { SubmitButton } from "@/components/ui/submit-button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { z } from "zod"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { signIn } from "next-auth/react"
import { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"

const schema = z.object({
  email: z.string().email({ message: "El formato de correo electrónico es inválido" }),
  password: z.string().min(6, { message: "La contraseña debe tener al menos 6 caracteres" })
    .max(20, { message: "La contraseña debe tener como máximo 20 caracteres" }),
})

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const registered = searchParams.get('registered');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(registered ? "Registro exitoso. Ahora puedes iniciar sesión." : null);
  const [isLoading, setIsLoading] = useState(false);
  
  const { register, handleSubmit, formState: { errors } } = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: z.infer<typeof schema>) => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const result = await signIn('credentials', {
        redirect: false,
        email: data.email,
        password: data.password,
      });
      
      if (result?.error) {
        setError('Credenciales inválidas. Por favor, inténtalo de nuevo.');
        setIsLoading(false);
      } else {
        // Redirigir al usuario después de iniciar sesión exitosamente
        router.push('/dashboard');
      }
    } catch (error) {
      setError('Ocurrió un error durante el inicio de sesión. Por favor, inténtalo de nuevo.');
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={cn("flex flex-col gap-6")}>
      <div className="flex flex-col items-center gap-2 text-center">
        <h1 className="text-2xl font-bold">Iniciar sesión</h1>
        <p className="text-muted-foreground text-sm text-balance">
          Inicia sesión con tu correo electrónico
        </p>
      </div>
      {error && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      {success && (
        <div className="p-3 bg-green-100 border border-green-400 text-green-700 rounded">
          {success}
        </div>
      )}
      <div className="grid gap-6">
        <div className="grid gap-3">
          <Label htmlFor="email">Correo electrónico</Label>
          <Input id="email" type="email" placeholder="me@example.com" {...register("email")} disabled={isLoading}/>
          {errors.email && <p className="text-red-500">{errors.email.message}</p>}
        </div>
        <div className="grid gap-3">
          <div className="flex items-center">
            <Label htmlFor="password">Contraseña</Label>
            <a
              href="#"
              className="ml-auto text-sm underline-offset-4 hover:underline"
            >
              ¿Olvidaste tu contraseña?
            </a>
          </div>
          <Input id="password" type="password" {...register("password")} disabled={isLoading}/>
          {errors.password && <p className="text-red-500">{errors.password.message}</p>}
        </div>
        <SubmitButton isPending={isLoading}>
          Iniciar sesión
        </SubmitButton>
      </div>
      <div className="text-center text-sm">
        ¿No tienes una cuenta?{" "}
        <Link href="/register" className="underline underline-offset-4">
          Regístrate
        </Link>
      </div>
    </form>
  )
}
