'use client'

import { cn } from "@/lib/utils"
import { SubmitButton } from "@/components/ui/submit-button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { z } from "zod"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { $apiV1 } from "@/api/api-v1"
import { Separator } from "@radix-ui/react-separator"
import { useEffect } from "react"

const schema = z.object({
  email: z.string().email({ message: "El formato de correo electrónico es inválido" }),
  password: z.string().min(6, { message: "La contraseña debe tener al menos 6 caracteres" })
    .max(20, { message: "La contraseña debe tener como máximo 20 caracteres" }),
  confirm_password: z.string().min(6, { message: "La contraseña debe tener al menos 6 caracteres" }),
  first_name: z.string().min(2, { message: "El nombre debe tener al menos 2 caracteres" }),
  last_name: z.string().min(2, { message: "El apellido debe tener al menos 2 caracteres" }),
  tenant_name: z.string().min(2, { message: "El nombre del inquilino debe tener al menos 2 caracteres" }),
  tenant_domain: z.string().min(2, { message: "El dominio del inquilino debe tener al menos 2 caracteres" }),
}).refine((data) => data.password === data.confirm_password, {
  message: "Las contraseñas no coinciden",
  path: ["confirm_password"],
});

export default function RegisterPage() {
  const router = useRouter();
  
  const { register, handleSubmit, formState: { errors }, watch } = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
  })

  const { mutateAsync: registerUser, isPending, error } = $apiV1.useMutation('post', '/auth/register', {
    onSuccess: () => {
      router.push('/login')
    }
  })

  const tenantName = watch('tenant_name')


  useEffect(() => {
    if (tenantName) {
      register('tenant_domain', {
        value: tenantName.toLowerCase().replace(/\s/g, '-'),
      })
    }
  }, [tenantName])

  const onSubmit = async (data: z.infer<typeof schema>) => {
    const response = await registerUser({ body: data })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={cn("flex flex-col gap-6")}>
      <div className="flex flex-col items-center gap-2 text-center">
        <h1 className="text-2xl font-bold">Crear cuenta</h1>
        <p className="text-muted-foreground text-sm text-balance">
          Regístrate para acceder a la plataforma
        </p>
      </div>
      {error && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          Error al registrar el usuario
        </div>
      )}
      <div className="grid gap-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-3">
            <Label htmlFor="first_name">Nombre</Label>
            <Input id="first_name" type="text" {...register("first_name")} disabled={isPending}/>
            {errors.first_name && <p className="text-red-500">{errors.first_name.message}</p>}
          </div>
          <div className="grid gap-3">
            <Label htmlFor="last_name">Apellido</Label>
            <Input id="last_name" type="text" {...register("last_name")} disabled={isPending}/>
            {errors.last_name && <p className="text-red-500">{errors.last_name.message}</p>}
          </div>
        </div>
        <div className="grid gap-3">
          <Label htmlFor="email">Correo electrónico</Label>
          <Input id="email" type="email" placeholder="me@example.com" {...register("email")} disabled={isPending}/>
          {errors.email && <p className="text-red-500">{errors.email.message}</p>}
        </div>
        <div className="grid gap-3">
          <Label htmlFor="password">Contraseña</Label>
          <Input id="password" type="password" {...register("password")} disabled={isPending}/>
          {errors.password && <p className="text-red-500">{errors.password.message}</p>}
        </div>
        <div className="grid gap-3">
          <Label htmlFor="confirm_password">Confirmar contraseña</Label>
          <Input id="confirm_password" type="password" {...register("confirm_password")} disabled={isPending}/>
          {errors.confirm_password && <p className="text-red-500">{errors.confirm_password.message}</p>}
        </div>
        <Separator /> 
        <h2 className="text-2xl font-bold">Inquilino</h2>
        <div className="grid gap-3">
          <Label htmlFor="tenant_name">Nombre</Label>
          <Input id="tenant_name" type="text" {...register("tenant_name")} disabled={isPending}/>
          {errors.tenant_name && <p className="text-red-500">{errors.tenant_name.message}</p>}
        </div>
        <div className="grid gap-3">
          <Label htmlFor="tenant_domain">Dominio</Label>
          <div className="flex gap-2 items-center">
            <Input id="tenant_domain" type="text" {...register("tenant_domain")} placeholder="example" disabled={isPending}/>
            <span className="text-muted-foreground">.localhost</span>
          </div>
          {errors.tenant_domain && <p className="text-red-500">{errors.tenant_domain.message}</p>}
        </div>
        <SubmitButton isPending={isPending}>
          Registrarse
        </SubmitButton>
      </div>
      <div className="text-center text-sm">
        ¿Ya tienes una cuenta?{" "}
        <Link href="/login" className="underline underline-offset-4">
          Iniciar sesión
        </Link>
      </div>
    </form>
  )
}
