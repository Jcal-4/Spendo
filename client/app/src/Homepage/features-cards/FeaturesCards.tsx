import { IconBusinessplan, IconMessageChatbot, IconLayoutDashboard } from '@tabler/icons-react';
import { Badge, Card, Container, Group, SimpleGrid, Text, Title, useMantineTheme } from '@mantine/core';
import classes from './FeaturesCards.module.css';

const mockdata = [
  {
    title: 'All Accounts, One Place',
    description:
      'Spendo operates independently, ensuring your transactions and accounts remain secure and private—no outside access. Enjoy an easy-to-use site to view and manage all your accounts in one place.',
    icon: IconBusinessplan,
  },
  {
    title: 'AI Chatbot Assistance',
    description:
      'Get instant financial advice and support with our integrated AI chatbot, available exclusively to logged-in users for your convenience.',
    icon: IconMessageChatbot,
  },
  {
    title: 'Personal Finance Dashboard',
    description:
      'Easily list all your personal banking accounts and transactions in one place. Spendo helps you track, analyze, and manage your money for smarter financial decisions.',
    icon: IconLayoutDashboard,
  },
];

export function FeaturesCards() {
  const theme = useMantineTheme();
  const features = mockdata.map((feature) => (
    <Card key={feature.title} shadow="md" radius="md" className={classes.card} padding="xl">
      <feature.icon size={50} stroke={1.5} color={theme.colors.blue[6]} />
      <Text fz="lg" fw={500} className={classes.cardTitle} mt="md">
        {feature.title}
      </Text>
      <Text fz="sm" c="dimmed" mt="sm">
        {feature.description}
      </Text>
    </Card>
  ));

  return (
    <Container size="lg" py="xl">
      <Group justify="center">
        {/* <Badge variant="filled" size="lg">
          Best company ever
        </Badge> */}
      </Group>

      <Title order={2} className={classes.title} ta="center" mt="sm">
        Your Personal Finance Hub: Accounts, AI Insights, and Dashboard
      </Title>

      {/* <Text c="dimmed" className={classes.description} ta="center" mt="md">
        Every once in a while, you’ll see a Golbat that’s missing some fangs. This happens when hunger drives it to try biting a Steel-type
        Pokémon.
      </Text> */}

      <SimpleGrid cols={{ base: 1, md: 3 }} spacing="xl" mt={50}>
        {features}
      </SimpleGrid>
    </Container>
  );
}

export default FeaturesCards;
