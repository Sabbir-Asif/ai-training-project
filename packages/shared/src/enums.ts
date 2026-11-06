import { z } from 'zod';

export const TaskStatus = z.enum(['TODO', 'IN_PROGRESS', 'DONE']);
export type TaskStatus = z.infer<typeof TaskStatus>;

export const Priority = z.enum(['LOW', 'MEDIUM', 'HIGH']);
export type Priority = z.infer<typeof Priority>;

export const TaskType = z.enum(['TASK', 'BUG']);
export type TaskType = z.infer<typeof TaskType>;
