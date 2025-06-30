'use client';

import { useSession } from 'next-auth/react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { $apiV1 } from '@/api/api-v1';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { SubmitButton } from '@/components/ui/submit-button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';

// Esquema de validación para el formulario de cambio de contraseña
const passwordFormSchema = z.object({
  current_password: z.string().min(1, {
    message: 'La contraseña actual es requerida.',
  }),
  new_password: z.string().min(8, {
    message: 'La nueva contraseña debe tener al menos 8 caracteres.',
  }),
  confirm_password: z.string().min(1, {
    message: 'La confirmación de contraseña es requerida.',
  }),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Las contraseñas no coinciden.",
  path: ["confirm_password"],
});

type PasswordFormValues = z.infer<typeof passwordFormSchema>;

export default function ChangePasswordPage() {
  const { data: session } = useSession();
  const router = useRouter();
  
  // Configurar el formulario con react-hook-form
  const form = useForm<PasswordFormValues>({
    resolver: zodResolver(passwordFormSchema),
    defaultValues: {
      current_password: '',
      new_password: '',
      confirm_password: '',
    },
  });

  const { mutateAsync: changePassword, isPending } = $apiV1.useMutation('post', '/change-password');

  // Función para manejar el envío del formulario
  async function onSubmit(data: PasswordFormValues) {
    try {
      await changePassword({
        body: {
          current_password: data.current_password,
          new_password: data.new_password,
        },
        headers: {
          Authorization: `Bearer ${session?.access_token}`
        }
      });
      toast.success('Contraseña actualizada correctamente', {
        duration: 3000,
      });
      // Redirigir al perfil después de cambiar la contraseña
      router.push('/profile');
    } catch (error) {
      toast.error('Error al cambiar la contraseña. Verifica que la contraseña actual sea correcta.');
    }
  }

  return (
    <div className="container max-w-2xl py-10">
      <Card>
        <CardHeader>
          <CardTitle>Cambiar Contraseña</CardTitle>
          <CardDescription>
            Actualiza tu contraseña para mantener segura tu cuenta.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="current_password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Contraseña Actual</FormLabel> 
                    <FormControl>
                      <Input type="password" placeholder="Ingresa tu contraseña actual" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="new_password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nueva Contraseña</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="Ingresa tu nueva contraseña" {...field} />
                    </FormControl>
                    <FormDescription>
                      La contraseña debe tener al menos 8 caracteres.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="confirm_password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Confirmar Contraseña</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="Confirma tu nueva contraseña" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <div className="flex justify-between">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => router.back()}
                >
                  Cancelar
                </Button>
                <SubmitButton
                  isPending={isPending}
                >
                  Cambiar Contraseña
                </SubmitButton>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
