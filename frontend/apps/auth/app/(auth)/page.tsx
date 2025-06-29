'use client';

import * as React from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { ArrowUpRight, Users, Building2, BarChart3, Activity } from 'lucide-react';

export default function AuthDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Usuarios Totales</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">245</div>
            <p className="text-xs text-muted-foreground">+12% desde el último mes</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Inquilinos Activos</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">18</div>
            <p className="text-xs text-muted-foreground">+2 desde el último mes</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tasa de Conversión</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24.3%</div>
            <p className="text-xs text-muted-foreground">+5.2% desde el último mes</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Actividad</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">573</div>
            <p className="text-xs text-muted-foreground">+201 desde el último mes</p>
          </CardContent>
        </Card>
      </div>

      <Separator />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Resumen General</CardTitle>
            <CardDescription>
              Información general del sistema de autenticación
            </CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            <div className="rounded-md bg-muted p-6 h-[200px] flex items-center justify-center">
              <p className="text-muted-foreground">Gráfico de actividad (placeholder)</p>
            </div>
          </CardContent>
        </Card>
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Actividad Reciente</CardTitle>
            <CardDescription>
              Últimos inicios de sesión y registros
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { user: 'Carlos Rodríguez', action: 'Inicio de sesión', time: 'Hace 5 minutos' },
                { user: 'Laura Gómez', action: 'Registro', time: 'Hace 15 minutos' },
                { user: 'Miguel Ángel', action: 'Inicio de sesión', time: 'Hace 32 minutos' },
                { user: 'Ana Martínez', action: 'Cambio de contraseña', time: 'Hace 1 hora' },
              ].map((item, index) => (
                <div key={index} className="flex items-center">
                  <div className="bg-primary text-primary-foreground flex h-9 w-9 items-center justify-center rounded-full">
                    {item.user.charAt(0)}
                  </div>
                  <div className="ml-4 space-y-1">
                    <p className="text-sm font-medium leading-none">{item.user}</p>
                    <p className="text-sm text-muted-foreground">{item.action}</p>
                  </div>
                  <div className="ml-auto font-medium text-sm text-muted-foreground">
                    {item.time}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
          <CardFooter>
            <a href="#" className="text-sm text-primary flex items-center">
              Ver toda la actividad
              <ArrowUpRight className="ml-1 h-4 w-4" />
            </a>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
