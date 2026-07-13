export function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <div className="rounded-lg border border-dashed border-border bg-surface-muted px-6 py-12 text-center">
      <p className="text-sm font-medium text-text">{title}</p>
      <p className="mt-1 text-sm text-muted-text">{message}</p>
    </div>
  );
}
