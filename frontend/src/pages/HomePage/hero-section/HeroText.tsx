import { Button, Container, Text, Title } from '@mantine/core';
import { Dots } from './Dots';
import classes from './HeroText.module.css';

export function HeroText() {
  return (
    <Container className={classes.wrapper} size={1400}>
      <Dots className={classes.dots} style={{ left: -380, top: 0 }} />
      <Dots className={classes.dots} style={{ left: -280, top: 0 }} />
      <Dots className={classes.dots} style={{ left: -380, top: 140 }} />
      <Dots className={classes.dots} style={{ right: -360, top: 60 }} />

      <div className={classes.inner}>
        <Title className={classes.title}>
          Smarter Personal Finance{' '}
          <Text component="span" className={classes.highlight} inherit>
            powered by AI
          </Text>{' '}
          for transaction management
        </Title>

        <Container p={0} size={600}>
          <Text size="lg" c="dimmed" className={classes.description}>
            A clean, feature-rich personal finance app focused on comprehensive financial insights and powerful transaction management.
          </Text>
        </Container>
{/* 
        <div className={classes.controls}>
          <Button className={classes.control} size="lg" variant="default" color="gray">
            Login
          </Button>
          <Button className={classes.control} size="lg">
            Register
          </Button>
        </div> */}
      </div>
    </Container>
  );
}

export default HeroText;
