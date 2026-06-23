import { RolesPage as RolesScreen } from "@/screens/roles/roles-page";

export default async function RolesPage({ params }: { params: Promise<{ login: string }> }) {
  const { login } = await params;

  return <RolesScreen login={decodeURIComponent(login)} />;
}
