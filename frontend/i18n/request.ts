import { getRequestConfig } from 'next-intl/server';
import enMessages from '../messages/en.json';

export default getRequestConfig(async () => {
  const locale = 'en';
  return {
    locale,
    messages: enMessages,
  };
});

