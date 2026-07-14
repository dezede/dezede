import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Skeleton from "@mui/material/Skeleton";

export default function EventCardSkeleton() {
  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Stack spacing={2}>
        <Stack spacing={0.5}>
          <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
            <Skeleton variant="text" width="38%" height={28} />
            <Skeleton variant="rounded" width={70} height={24} />
          </Stack>
          <Stack direction="row" spacing={1}>
            <Skeleton variant="rounded" width={130} height={24} />
          </Stack>
        </Stack>
        <Stack spacing={0.75}>
          <Skeleton variant="text" width="18%" height={16} />
          <Stack direction="row" spacing={0.5} useFlexGap sx={{ flexWrap: "wrap" }}>
            <Skeleton variant="rounded" width={90} height={24} />
            <Skeleton variant="rounded" width={110} height={24} />
            <Skeleton variant="rounded" width={80} height={24} />
          </Stack>
        </Stack>
        <Stack spacing={0.75}>
          <Skeleton variant="text" width="15%" height={16} />
          <Skeleton variant="text" width="85%" />
          <Skeleton variant="text" width="70%" />
          <Skeleton variant="text" width="55%" />
        </Stack>
      </Stack>
    </Paper>
  );
}
