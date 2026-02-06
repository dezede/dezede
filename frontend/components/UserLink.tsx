import { TRelatedUser } from "@/app/types";
import SmallCaps from "@/format/SmallCaps";

export function UserLabel({ user }: { user: TRelatedUser }) {
  return (
    <>
      {user.first_name} <SmallCaps>{user.last_name}</SmallCaps>
    </>
  );
}

export default function UserLink({ user }: { user: TRelatedUser }) {
  return (
    <a href={`/utilisateurs/${user.username}`}>
      <UserLabel user={user} />
    </a>
  );
}
