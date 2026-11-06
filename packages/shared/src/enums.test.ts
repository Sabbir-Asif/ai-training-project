import { describe, expect, it } from 'vitest';
import { Priority, TaskStatus, TaskType } from './enums';

describe('shared enums', () => {
  it('accepts valid values and rejects invalid ones', () => {
    expect(TaskStatus.parse('TODO')).toBe('TODO');
    expect(Priority.safeParse('URGENT').success).toBe(false);
    expect(TaskType.options).toEqual(['TASK', 'BUG']);
  });
});
