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
    useMantineTheme,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import classes from './HeaderMegaMenu.module.css';
import ThemeToggle from '../theme-toggle/ThemeToggle';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/useAuth';


export function HeaderMegaMenu() {
    const [drawerOpened, { toggle: toggleDrawer, close: closeDrawer }] = useDisclosure(false);
    const [linksOpened, { toggle: toggleLinks }] = useDisclosure(false);
    const theme = useMantineTheme();
    const navigate = useNavigate();
    const [state, { logout }] = useAuth();


    const redirectURL = (URL) => {
        console.log('URL--> ', URL);
        if (URL === 'LOGIN') {
            navigate('/login');
        }
    };

    return (
        <Box >
            <header className={classes.header}>
                <Group justify="space-between" h="100%">
                    <Group>
                        <ThemeToggle />
                    </Group>
                    <Group h="100%" gap={0} visibleFrom="sm">
                        <Text size="xl" fw={900} variant="gradient" gradient={{ from: 'cyan', to: 'green', deg: 332 }}>
                            Spendo
                        </Text>
                    </Group>

                    <Group visibleFrom="sm">
                        {state.isAuthenticated && state.user ? (
                            <div style={{ display: 'flex' }}>
                                <Text size="xl" fw={900} variant="gradient" gradient={{ from: 'cyan', to: 'green', deg: 332 }}>
                                    Welcome, {state.user.username}!
                                </Text>
                                {/* <Button onClick={logout} variant="default">
                                    Logout
                                </Button> */}
                            </div>
                        ) : (
                            <Button onClick={() => redirectURL('LOGIN')} variant="default">
                                Log in
                            </Button>
                        )}
                        {/* <Button>Sign up</Button> */}
                    </Group>
                </Group>
            </header>
        </Box>
    );
}

export default HeaderMegaMenu;
