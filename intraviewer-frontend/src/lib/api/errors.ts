interface ApiErrorShape {
  response?: {
    status?: number;
    data?: { message?: string };
  };
}

/** Reads `error.response.data.message` (axios shape) with a fallback. */
export function getApiErrorMessage(error: unknown, fallback: string): string {
  return (error as ApiErrorShape | undefined)?.response?.data?.message || fallback;
}

/** Reads `error.response.status` (axios shape). */
export function getApiErrorStatus(error: unknown): number | undefined {
  return (error as ApiErrorShape | undefined)?.response?.status;
}
