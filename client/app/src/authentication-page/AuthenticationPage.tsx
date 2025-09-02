import { Anchor, Button, Checkbox, Paper, PasswordInput, Text, TextInput, Title } from '@mantine/core';
import classes from './AuthenticationPage.module.css';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/useAuth';

const apiUrl = import.meta.env.VITE_API_URL;

export function AuthenticationPage() {
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState<boolean>(false);
  const [state, { login }] = useAuth();
  const [form, setForm] = useState({ username: '', password: '' });
  const [registerForm, setRegisterForm] = useState({
    email: '',
    username: '',
    first_name: '',
    last_name: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log(form);
  }, [form]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  };

  const handleRegisterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRegisterForm({ ...registerForm, [e.target.name]: e.target.value });
  };

  const loginUser = async (e: React.FormEvent) => {
    console.log('handling submit');
    e.preventDefault();
    
    try {
      await login(form);
      navigate('/');
    } catch (e) {
      setError('Invalid credentials.' + e);
      console.log(error);
    }
  };

  const createUser = async (e: React.FormEvent) => {
    console.log('handling creation');
    console.log(registerForm);
    e.preventDefault();
    try {
      const response = await fetch(`${apiUrl}/createuser/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerForm),
      });
      const data = await response.json();
      console.log(data);
      console.log('User Created!');
      navigate('/');
    } catch (e) {
      setError('Invalid credentials.' + e);
      console.log(error);
    }
  };

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
            <form onSubmit={loginUser}>
              <TextInput name="username" onChange={handleChange} label="Username" placeholder="Your Username" size="md" radius="md" />
              <PasswordInput
                name="password"
                onChange={handleChange}
                label="Password"
                placeholder="Your password"
                mt="md"
                size="md"
                radius="md"
              />
              <Checkbox label="Keep me logged in" mt="xl" size="md" />
              <Button type="submit" fullWidth mt="xl" size="md" radius="md">
                Login
              </Button>
            </form>

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
            <form onSubmit={createUser}>
              <TextInput
                name="email"
                value={registerForm.email}
                onChange={handleRegisterChange}
                label="Email address"
                placeholder="hello@gmail.com"
                size="md"
                radius="md"
              />
              <TextInput
                name="username"
                value={registerForm.username}
                onChange={handleRegisterChange}
                label="Username"
                placeholder="jDoe1"
                size="md"
                radius="md"
              />
              <TextInput
                name="first_name"
                value={registerForm.first_name}
                onChange={handleRegisterChange}
                label="First Name"
                placeholder="John"
                size="md"
                radius="md"
              />
              <TextInput
                name="last_name"
                value={registerForm.last_name}
                onChange={handleRegisterChange}
                label="Last Name"
                placeholder="Doe"
                size="md"
                radius="md"
              />
              <PasswordInput
                name="password"
                value={registerForm.password}
                onChange={handleRegisterChange}
                label="Create password"
                placeholder="Create password"
                mt="md"
                size="md"
                radius="md"
              />
              <PasswordInput
                name="confirmPassword"
                value={registerForm.confirmPassword}
                onChange={handleRegisterChange}
                label="Confirm Password"
                placeholder="Confirm Password"
                mt="md"
                size="md"
                radius="md"
              />
              <Button type="submit" fullWidth mt="xl" size="md" radius="md">
                Register
              </Button>
            </form>
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
