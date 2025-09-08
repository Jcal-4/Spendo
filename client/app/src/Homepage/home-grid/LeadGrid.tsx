import { IconArrowDownRight, IconDiscount2 } from '@tabler/icons-react';
import { Group, Paper, Text } from '@mantine/core';
import StatsSegments from './stats-segments/StatsSegments';
import Demo from './chart/Chart';

interface StatsSegmentsProps {
  user_balance: {
    cash_balance?: number;
    savings_balance?: number;
    investing_retirement?: number;
    total_balance?: number;
  };
}

export function LeadGrid(props: StatsSegmentsProps) {
  return (
    <div className="flex flex-row items-center justify-center gap-8 min-w-full !p-10">
      <div className="flex-1 ">
        <Paper withBorder p="md" radius="md">
          <Demo />
        </Paper>
      </div>

      <div className="flex flex-1 flex-col gap-6">
        <StatsSegments user_balance={props.user_balance} />
        <div className="flex w-full gap-6">
          <div className="flex-1">
            <Paper withBorder p="md" radius="md">
              <Group justify="space-between">
                <Text size="xs" c="dimmed">
                  34.17
                </Text>
                <IconDiscount2 size={22} stroke={1.5} />
              </Group>

              <Group align="flex-end" gap="xs" mt={25}>
                <Text className="text-2xl font-bold">1230</Text>
                <Text c="teal" fz="sm" fw={500}>
                  <span>34.19%</span>
                  <IconArrowDownRight size={16} stroke={1.5} />
                </Text>
              </Group>

              <Text fz="xs" c="dimmed" mt={7}>
                Compared to previous month
              </Text>
            </Paper>
          </div>

          <div className="flex-1">
            <Paper withBorder p="md" radius="md">
              <Group justify="space-between">
                <Text size="xs" c="dimmed">
                  34.17
                </Text>
                <IconDiscount2 size={22} stroke={1.5} />
              </Group>

              <Group align="flex-end" gap="xs" mt={25}>
                <Text className="text-2xl font-bold">1230</Text>
                <Text c="teal" fz="sm" fw={500}>
                  <span>34.19%</span>
                  <IconArrowDownRight size={16} stroke={1.5} />
                </Text>
              </Group>

              <Text fz="xs" c="dimmed" mt={7}>
                Compared to previous month
              </Text>
            </Paper>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LeadGrid;
