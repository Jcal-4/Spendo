import { useState } from 'react';
import {
    IconCalendarStats,
    IconDeviceDesktopAnalytics,
    IconFingerprint,
    IconGauge,
    IconHome2,
    IconLogout,
    IconSettings,
    IconSwitchHorizontal,
    IconUser,
} from '@tabler/icons-react';
import { Center, Stack, Tooltip, UnstyledButton } from '@mantine/core';
import classes from './NavbarMinimal.module.css';
import { useAuth } from '../../contexts/useAuth';

interface NavbarLinkProps {
    icon: typeof IconHome2;
    label: string;
    active?: boolean;
    onClick?: () => void;
}

function NavbarLink({ icon: Icon, label, active, onClick }: NavbarLinkProps) {
    return (
        <Tooltip label={label} position="right" transitionProps={{ duration: 0 }}>
            <UnstyledButton onClick={onClick} className={classes.link} data-active={active || undefined}>
                <Icon size={20} stroke={1.5} />
            </UnstyledButton>
        </Tooltip>
    );
}

const mockdata = [
    { icon: IconHome2, label: 'Home' },
    { icon: IconGauge, label: 'Dashboard' },
    { icon: IconDeviceDesktopAnalytics, label: 'Analytics' },
    { icon: IconCalendarStats, label: 'Releases' },
    { icon: IconUser, label: 'Account' },
    { icon: IconFingerprint, label: 'Security' },
    { icon: IconSettings, label: 'Settings' },
];

export function NavbarMinimal() {
    const [state, { logout }] = useAuth();
    const [active, setActive] = useState(2);

    const links = mockdata.map((link, index) => (
        <NavbarLink {...link} key={link.label} active={index === active} onClick={() => setActive(index)} />
    ));

    return (
        <>
            {state.isAuthenticated && state.user ? (
                <nav className={classes.navbar}>
                    <Center></Center>

                    <div className={classes.navbarMain}>
                        <Stack justify="center" gap={0}>
                            {links}
                        </Stack>
                    </div>

                    <Stack justify="center" gap={0}>
                        <NavbarLink onClick={logout} icon={IconLogout} label="Logout" />
                    </Stack>
                </nav>
            ) : (
                <></>
            )}
        </>
    );
}

export default NavbarMinimal;
