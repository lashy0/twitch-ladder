import { FollowPage } from "@/screens/follow/follow-page";

export default async function FollowRoute({ params }: { params: Promise<{ login: string }> }) {
  const { login } = await params;

  return <FollowPage login={decodeURIComponent(login)} />;
}
