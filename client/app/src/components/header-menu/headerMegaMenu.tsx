import { IconBook, IconChartPie3, IconChevronDown, IconCode, IconCoin, IconFingerprint, IconNotification } from '@tabler/icons-react';
import {
    Anchor,
    Box,
    Burger,
    Button,
    Center,
    Collapse,
    Divider,
    Drawer,
    Group,
    HoverCard,
    ScrollArea,
    SimpleGrid,
    Text,
    ThemeIcon,
    UnstyledButton,
    useMantineTheme
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import classes from './HeaderMegaMenu.module.css';
import ThemeToggle from '../theme-toggle/ThemeToggle';
import { useNavigate } from 'react-router-dom';

const mockdata = [
    {
        icon: IconCode,
        title: 'Open source',
        description: 'This Pokémon’s cry is very loud and distracting',
    },
    {
        icon: IconCoin,
        title: 'Free for everyone',
        description: 'The fluid of Smeargle’s tail secretions changes',
    },
    {
        icon: IconBook,
        title: 'Documentation',
        description: 'Yanma is capable of seeing 360 degrees without',
    },
    {
        icon: IconFingerprint,
        title: 'Security',
        description: 'The shell’s rounded shape and the grooves on its.',
    },
    {
        icon: IconChartPie3,
        title: 'Analytics',
        description: 'This Pokémon uses its flying ability to quickly chase',
    },
    {
        icon: IconNotification,
        title: 'Notifications',
        description: 'Combusken battles with the intensely hot flames it spews',
    },
];

export function HeaderMegaMenu() {
    const [drawerOpened, { toggle: toggleDrawer, close: closeDrawer }] = useDisclosure(false);
    const [linksOpened, { toggle: toggleLinks }] = useDisclosure(false);
    const theme = useMantineTheme();
    const navigate = useNavigate();
    
    const links = mockdata.map((item) => (
        <UnstyledButton className={classes.subLink} key={item.title}>
            <Group wrap="nowrap" align="flex-start">
                <ThemeIcon size={34} variant="default" radius="md">
                    <item.icon size={22} color={theme.colors.blue[6]} />
                </ThemeIcon>
                <div>
                    <Text size="sm" fw={500}>
                        {item.title}
                    </Text>
                    <Text size="xs" c="dimmed">
                        {item.description}
                    </Text>
                </div>
            </Group>
        </UnstyledButton>
    ));

    const redirectURL = (URL) => {
        console.log('URL--> ' , URL)
        if (URL === 'LOGIN') {
            navigate('/login')
        }
    }

    return (
        <Box pb={120}>
            <header className={classes.header}>
                <Group justify="space-between" h="100%">
                    <ThemeToggle />
                    <Group h="100%" gap={0} visibleFrom="sm">
                        <Text size="xl" fw={900} variant="gradient" gradient={{ from: 'cyan', to: 'green', deg: 332 }}>
                            Spendo
                        </Text>
                    </Group>

                    <Group visibleFrom="sm">
                        <Button onClick={() => redirectURL('LOGIN')} variant="default">
                            Log in
                        </Button>
                        <Button>Sign up</Button>
                    </Group>

                    <Burger opened={drawerOpened} onClick={toggleDrawer} hiddenFrom="sm" />
                </Group>
            </header>
        </Box>
    );
}

export default HeaderMegaMenu;
