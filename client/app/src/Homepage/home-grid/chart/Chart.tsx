'use client';

import { Chart, useChart } from '@chakra-ui/charts';
import { CartesianGrid, Line, LineChart, Tooltip, XAxis, YAxis } from 'recharts';

const Demo = () => {
  const chart = useChart({
    data: [
      { sale: 10, month: 'January' },
      { sale: 95, month: 'February' },
      { sale: 87, month: 'March' },
      { sale: 88, month: 'May' },
      { sale: 65, month: 'June' },
      { sale: 90, month: 'August' },
    ],
    series: [{ name: 'sale', color: 'teal.solid' }],
  });

  return (
    <Chart.Root className="w-full max-w-xl h-94 mx-auto" chart={chart}>
      <LineChart data={chart.data}>
        <CartesianGrid stroke="#424242" vertical={false} />
        <XAxis axisLine={false} dataKey={chart.key('month')} tickFormatter={(value) => value.slice(0, 3)} stroke={chart.color('border')} />
        <YAxis axisLine={false} tickLine={false} tickMargin={10} stroke={chart.color('border')} />
        <Tooltip animationDuration={100} cursor={false} content={<Chart.Tooltip />} />
        {chart.series.map((item) => (
          <Line
            key={item.name}
            isAnimationActive={false}
            dataKey={chart.key(item.name)}
            stroke={chart.color(item.color)}
            strokeWidth={2}
            dot={false}
          />
        ))}
      </LineChart>
    </Chart.Root>
  );
};
export default Demo;
