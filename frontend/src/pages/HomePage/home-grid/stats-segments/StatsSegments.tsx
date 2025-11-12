import { useState } from 'react';
import { IconDeviceAnalytics } from '@tabler/icons-react';
import { Box, Group, Paper, Progress, SimpleGrid, Text } from '@mantine/core';
import classes from './StatsSegments.module.css';

interface StatsSegmentsProps {
  user_balance: {
    cash_balance?: number;
    savings_balance?: number;
    investing_retirement?: number;
    total_balance?: number;
  };
}

export function StatsSegments(props: StatsSegmentsProps) {
  // Helper to format numbers with commas
  const formatMoney = (amount: number) => amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const { cash_balance = 0, savings_balance = 0, investing_retirement = 0, total_balance = 0 } = props.user_balance;

  // Calculate percentages so they always sum to 100%
  let cashPercent = 0,
    savingsPercent = 0,
    investPercent = 0;
  if (total_balance > 0) {
    cashPercent = Math.round((cash_balance / total_balance) * 100);
    savingsPercent = Math.round((savings_balance / total_balance) * 100);
    investPercent = 100 - cashPercent - savingsPercent;
  }

  const data = [
    { label: 'Cash', count: cash_balance, part: cashPercent, color: '#47d6ab' },
    { label: 'Savings', count: savings_balance, part: savingsPercent, color: '#ffb347' }, // orange
    { label: 'Investing & Retirement', count: investing_retirement, part: investPercent, color: '#4fcdf7' },
  ];
  // const [totalMonetaryValue, setTotalMonetaryValue] = useState(0);
  const segments = data.map((segment) => (
    <Progress.Section value={segment.part} color={segment.color} key={segment.color}>
      {segment.part > 10 && <Progress.Label>{segment.part}%</Progress.Label>}
    </Progress.Section>
  ));

  const descriptions = data.map((stat) => (
    <Box key={stat.label} style={{ borderBottomColor: stat.color }} className={classes.stat}>
      <Text tt="uppercase" fz="xs" c="dimmed" fw={700}>
        {stat.label}
      </Text>

      <Group justify="space-between" align="flex-end" gap={0}>
        <Text fw={700}>${formatMoney(stat.count)}</Text>
        <Text c={stat.color} fw={700} size="sm" className={classes.statCount}>
          {stat.part}%
        </Text>
      </Group>
    </Box>
  ));

  return (
    <Paper withBorder p="md" radius="md">
      <Group justify="space-between">
        <Group align="flex-end" gap="xs">
          <Text fz="xl" fw={700}>
            ${formatMoney(total_balance)}
          </Text>
          {/* <Text c="teal" className={classes.diff} fz="sm" fw={700}>
            <span>18%</span>
            <IconArrowUpRight size={16} style={{ marginBottom: 4 }} stroke={1.5} />
          </Text> */}
        </Group>
        <IconDeviceAnalytics size={22} className={classes.icon} stroke={1.5} />
      </Group>

      <Text c="dimmed" fz="sm">
        Total Monetary Balance
      </Text>

      <Progress.Root size={34} classNames={{ label: classes.progressLabel }} mt={40}>
        {segments}
      </Progress.Root>
      <SimpleGrid cols={{ base: 1, xs: 3 }} mt="xl">
        {descriptions}
      </SimpleGrid>
    </Paper>
  );
}

export default StatsSegments;
