import { TRelatedUser } from "@/app/types";
import SmallCaps from "@/format/SmallCaps";

export default function UserLink({ user }: { user: TRelatedUser }) {
  return (
    <a href={`/utilisateurs/${user.username}`}>
      {user.first_name} <SmallCaps>{user.last_name}</SmallCaps>
    </a>
  );
}
