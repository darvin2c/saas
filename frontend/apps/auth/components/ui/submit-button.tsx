

import { Button } from "./button";

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
            {isPending ? "Enviando..." : children}
        </Button>
    )
}