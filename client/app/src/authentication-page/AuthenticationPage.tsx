import { Anchor, Button, Checkbox, Paper, PasswordInput, Text, TextInput, Title } from '@mantine/core';
import classes from './AuthenticationPage.module.css';
import { useEffect, useState } from 'react';

export function AuthenticationPage() {
    const [isRegister, setIsRegister] = useState<boolean>(false);

    useEffect(() => {
        console.log(isRegister);
    }, []);

    const startRegistration = (): void => {
        setIsRegister(true);
    };

    const startLogin = (): void => {
        setIsRegister(false);
    };

    return (
        <>
            {!isRegister ? (
                <div className={classes.wrapper}>
                    <Paper className={classes.form}>
                        <Title order={2} className={classes.title}>
                            Welcome back to Spendo!
                        </Title>

                        <TextInput label="Email address" placeholder="hello@gmail.com" size="md" radius="md" />
                        <PasswordInput label="Password" placeholder="Your password" mt="md" size="md" radius="md" />
                        <Checkbox label="Keep me logged in" mt="xl" size="md" />
                        <Button fullWidth mt="xl" size="md" radius="md">
                            Login
                        </Button>

                        <Text ta="center" mt="md">
                            Don&apos;t have an account?{' '}
                            <Anchor href="#" fw={500} onClick={startRegistration}>
                                Register
                            </Anchor>
                        </Text>
                    </Paper>
                </div>
            ) : (
                <div className={classes.wrapper}>
                    <Paper className={classes.form}>
                        <Title order={2} className={classes.title}>
                            Welcome to Spendo!
                        </Title>

                        <TextInput label="Email address" placeholder="hello@gmail.com" size="md" radius="md" />
                        <PasswordInput label="Create password" placeholder="Create password" mt="md" size="md" radius="md" />
                        <PasswordInput label="Confirm Password" placeholder="Confirm Password" mt="md" size="md" radius="md" />
                        <Button fullWidth mt="xl" size="md" radius="md">
                            Register
                        </Button>

                        <Text ta="center" mt="md">
                            Already have an account?{' '}
                            <Anchor href="#" fw={500} onClick={startLogin}>
                                Login
                            </Anchor>
                        </Text>
                    </Paper>
                </div>
            )}
        </>
    );
}

export default AuthenticationPage;
