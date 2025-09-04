import { Container, Grid, SimpleGrid, Skeleton } from '@mantine/core';
import StatsSegments from './stats-segments/StatsSegments';
const PRIMARY_COL_HEIGHT = '300px';

export function LeadGrid() {
  const SECONDARY_COL_HEIGHT = `calc(${PRIMARY_COL_HEIGHT} / 2 - var(--mantine-spacing-md) / 2)`;

  return (
    <div className="flex flex-row items-center justify-center gap-8 m-8">
      <div>
        <StatsSegments />
      </div>
      <div className="flex flex-col gap-6">
        <StatsSegments />
        <div className="flex gap-6">
          <Skeleton height={SECONDARY_COL_HEIGHT} radius="md" animate={false} />
          <Skeleton height={SECONDARY_COL_HEIGHT} radius="md" animate={false} />
        </div>
      </div>
    </div>
  );
}

export default LeadGrid;
