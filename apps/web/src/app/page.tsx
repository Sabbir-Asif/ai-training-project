import { TaskStatus } from '@devpulse/shared';

export default function Home() {
  return (
    <main>
      <h1>DevPulse</h1>
      <p>Statuses: {TaskStatus.options.join(', ')}</p>
    </main>
  );
}
