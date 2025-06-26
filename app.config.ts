import { ConfigContext, ExpoConfig } from '@expo/config';
import 'dotenv/config';

export default ({ config }: ConfigContext): ExpoConfig => {
  const apiUrl = process.env.API_URL;
  if (!apiUrl) throw new Error("API_URL tanımı yok!");
  return {
    ...config,
    extra: { apiUrl },
  } as ExpoConfig;
};