'use client';

import { useSession } from 'next-auth/react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
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
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'sonner';

// Esquema de validación para el formulario
const profileFormSchema = z.object({
  first_name: z.string().min(1, {
    message: 'El nombre es requerido.',
  }),
  last_name: z.string().min(1, {
    message: 'El apellido es requerido.',
  }),
});

type ProfileFormValues = z.infer<typeof profileFormSchema>;

export default function EditProfilePage() {
  const { data: session } = useSession();
  const router = useRouter();
  const queryClient = useQueryClient();
  
  // Obtener los datos del usuario
  const { data: user, isLoading } = $apiV1.useQuery('get', '/users/me', 
    {
      headers: {
        Authorization: `Bearer ${session?.access_token}`
      }
    }, {
      enabled: !!session?.access_token
    }
  );

  // Configurar el formulario con react-hook-form
  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileFormSchema),
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
    },
    values: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
    },
  });

  const { mutateAsync: updateProfile, isPending } = $apiV1.useMutation('patch', '/users/me');

  // Función para manejar el envío del formulario
  async function onSubmit(data: ProfileFormValues) {
    await updateProfile({
      body: data,
      headers: {
        Authorization: `Bearer ${session?.access_token}`
      }
    }, {
      onSuccess: () => {
        toast.success('Perfil actualizado correctamente', {
          duration: 3000,
          
        });
        // invalidate the query
        queryClient.invalidateQueries({
          queryKey: ['get', '/users/me'],
        });
      },
      onError: () => {
        toast.error('Error al actualizar el perfil');
      }
    });
  }

  // Mostrar un esqueleto mientras se cargan los datos
  if (isLoading) {
    return (
      <div className="container max-w-2xl py-10">
        <Card>
          <CardHeader>
            <Skeleton className="h-8 w-64 mb-2" />
            <Skeleton className="h-4 w-full" />
          </CardHeader>
          <CardContent className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-10 w-full" />
              </div>
            ))}
          </CardContent>
          <CardFooter>
            <Skeleton className="h-10 w-32" />
          </CardFooter>
        </Card>
      </div>
    );
  }

  return (
    <div className="container max-w-2xl py-10">
      <Card>
        <CardHeader>
          <CardTitle>Editar Perfil</CardTitle>
          <CardDescription>
            Actualiza tu información personal. Tu correo electrónico se usa para iniciar sesión.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nombre</FormLabel> 
                    <FormControl>
                      <Input placeholder="Tu nombre" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="last_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Apellido</FormLabel>
                    <FormControl>
                      <Input placeholder="Tu apellido" {...field} />
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
                  Guardar cambios
                </SubmitButton>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}