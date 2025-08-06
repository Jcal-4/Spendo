import { IconAt, IconPhoneCall } from '@tabler/icons-react';
import { Avatar, Group, Text } from '@mantine/core';
import classes from './UserInfoIcons.module.css';

export function UserInfoIcons() {
    return (
        <div>
            <Group wrap="nowrap">
                <Avatar
                    src="https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-3.png"
                    size={68}
                    radius="lg"
                />
                <div>
                    <Text fz="xs" tt="uppercase" fw={700} c="dimmed">
                        Software engineer
                    </Text>

                    <Text fz="lg" fw={500} className={classes.name}>
                        Jairo Calderon
                    </Text>

                    <Group wrap="nowrap" gap={10} mt={3}>
                        <Text fz="xs" c="dimmed">
                            Jairo.Calderon.Dev@protonmail.com
                        </Text>
                    </Group>
                </div>
            </Group>
        </div>
    );
}

export default UserInfoIcons;