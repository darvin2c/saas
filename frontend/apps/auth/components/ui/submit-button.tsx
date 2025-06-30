

import { Button } from "./button";
import { Loader2 } from "lucide-react";

export function SubmitButton(
    {
        isPending,
        children,
    }: {
        isPending: boolean;
        children: React.ReactNode;
    }
) {
    return (
        <Button
            type="submit"
            disabled={isPending}
        >
            {isPending ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Enviando</> : children}
        </Button>
    )
}