'use client';

import { Tabs, TabsContents, TabsList, TabsTrigger } from "@/components/animate-ui/radix/tabs";
import { usePathname } from "next/navigation";
import Link from "next/link";

export default function ProfileLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();
    return (
        <div className="mx-auto rounded-lg px-2">
            <Tabs
                value={pathname}
            >
                <TabsList>
                    <Link href="/profile"><TabsTrigger value="/profile">Información Personal</TabsTrigger></Link>
                    <Link href="/profile/change-password"><TabsTrigger value="/profile/change-password">Cambiar Contraseña</TabsTrigger></Link>
                </TabsList>
                <TabsContents>
                    {children}
                </TabsContents>
            </Tabs>
        </div>
    );
}