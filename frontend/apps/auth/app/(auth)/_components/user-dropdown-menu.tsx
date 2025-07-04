'use client';

import {
  User,
  Lock,
  Bell,
  Settings,
  Grid,
  HelpCircle,
  LogOut,
  ChevronsUpDown
} from 'lucide-react';

import {
  SidebarMenuButton,
} from '@/components/animate-ui/radix/sidebar';

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/animate-ui/radix/dropdown-menu';
import { $apiV1 } from '@/api/api-v1';
import { signOut, useSession } from 'next-auth/react';
import { Skeleton } from '@/components/ui/skeleton';
import Link from 'next/link';



export function UserDropdownMenu() {
  const { data: session } = useSession()
  const { data: user } = $apiV1.useQuery('get', '/users/me',
    {
      headers: {
        Authorization: `Bearer ${session?.access_token}`
      }
    }, {
      enabled: !!session?.access_token
    }
  )
  
  if(!user){
     // skeleton 
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <SidebarMenuButton size="lg">
            <Skeleton className="size-8 rounded-full" />
            <Skeleton className="h-4 w-24" />
          </SidebarMenuButton>
        </DropdownMenuTrigger>
      </DropdownMenu>
    )
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <SidebarMenuButton size="lg">
          <div className="bg-muted size-8 rounded-full flex items-center justify-center text-foreground font-medium">
            {user?.first_name?.charAt(0).toUpperCase()}
          </div>
          <div className="grid flex-1 text-left text-sm leading-tight">
            <span className="truncate font-semibold">{user?.first_name}</span>
            <span className="truncate text-xs text-muted-foreground">{user?.email}</span>
          </div>
          <ChevronsUpDown className="ml-auto size-4" />
        </SidebarMenuButton>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="center">
        <DropdownMenuLabel>Mi Cuenta</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem>
            <Link href="/profile"
              className="flex items-center gap-2"
            >
              <User className="mr-2 size-4" />
              <span>Editar Perfil</span>
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem>
            <Link href="/profile/change-password"
              className="flex items-center gap-2"
            >
              <Lock className="mr-2 size-4" />
              <span>Cambiar Contraseña</span>
            </Link>
          </DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem>
            <HelpCircle className="mr-2 size-4" />
            <span>Ayuda</span>
          </DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem variant="destructive"
          onClick={() => signOut()}
        >
          <LogOut className="mr-2 size-4" />
          <span>Cerrar Sesión</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
