import Link from "next/link";

export default async function RolesPage({ params }: { params: Promise<{ login: string }> }) {
  const { login } = await params;

  return (
    <main className="min-h-dvh bg-[var(--color-app-bg)] p-8 text-white">
      <Link className="text-[var(--color-app-accent)]" href="/">
        На главную
      </Link>
      <h1 className="mt-8 text-3xl font-semibold">Роли: @{decodeURIComponent(login)}</h1>
    </main>
  );
}
