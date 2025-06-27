

import { Button } from "./button";

export function SubmitButton(
    {
        isLoading,
        children,
    }: {
        isLoading: boolean;
        children: React.ReactNode;
    }
) {
    return (
        <Button
            type="submit"
            disabled={isLoading}
        >
            {isLoading ? "Enviando..." : children}
        </Button>
    )
}