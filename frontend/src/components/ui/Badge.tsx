export function Badge({ children }: { children: string }) {
  return (
    <span className="px-2 py-0.5 rounded-full text-xs glass inline-block">
      {children}
    </span>
  );
}


